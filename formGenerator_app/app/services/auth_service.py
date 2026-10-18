import os
import sys

# Evita o crash rígido (ScopeChangedError) caso o Google retorne escopos diferentes dos pedidos
os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class InsufficientPermissionsError(Exception):
    """Lançada quando o usuário não concede as permissões essenciais de Drive ou Forms no Google."""
    def __init__(self, missing_permissions=None):
        self.missing_permissions = missing_permissions or ["Google Drive", "Google Formulários"]
        msg = f"Permissões faltantes: {', '.join(self.missing_permissions)}"
        super().__init__(msg)


def get_credentials_path(filename):
    """
    Retorna o caminho dinâmico para os arquivos de credenciais.
    - token.json: Salvo na pasta do usuário (~/.form_generator) para persistência e permissão.
    - client_secret.json: Lido da pasta temporária (sys._MEIPASS) se frozen, ou localmente em dev.
    """
    if filename == "token.json":
        user_dir = os.path.expanduser("~/.form_generator")
        os.makedirs(user_dir, exist_ok=True)
        return os.path.join(user_dir, "token.json")
    
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        return os.path.join(base_path, "credentials", filename)
    else:
        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )
        )
        return os.path.join(base_dir, "credentials", filename)


TOKEN_PATH = get_credentials_path("token.json")
CLIENT_SECRET_PATH = get_credentials_path("client_secret.json")


SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]


_active_server = None
_login_cancelled = False


def save_token(creds, granted_scopes=None):
    """Salva o token e os escopos efetivamente concedidos em token.json."""
    import json
    token_dict = json.loads(creds.to_json())
    if granted_scopes:
        token_dict["granted_scopes"] = list(granted_scopes)
    with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
        json.dump(token_dict, token_file, indent=2)


def get_actual_granted_scopes(creds, session_token=None) -> set[str]:
    """
    Retorna o conjunto de escopos REALMENTE concedidos pelo usuário/Google.
    Nota: creds.scopes armazena apenas os escopos que foram solicitados originalmente.
    Os escopos efetivamente autorizados pelo usuário ficam em session_token,
    creds.granted_scopes, no arquivo token.json local ou via endpoint tokeninfo.
    """
    scopes_found = set()

    # 1. Se session_token estiver disponível (logo após o fluxo OAuth interativo)
    if session_token:
        # Se for um OAuth2Token ou objeto com atributo 'scopes'
        if hasattr(session_token, "scopes") and session_token.scopes:
            for s in session_token.scopes:
                if isinstance(s, str):
                    scopes_found.update(s.split())
        elif isinstance(session_token, dict) and "scope" in session_token:
            s = session_token["scope"]
            if isinstance(s, str):
                scopes_found.update(s.split())
            elif isinstance(s, (list, tuple, set)):
                for item in s:
                    if isinstance(item, str):
                        scopes_found.update(item.split())

    # 2. Se creds.granted_scopes estiver preenchido (objeto Credentials gerado pelo helper)
    if not scopes_found and hasattr(creds, "granted_scopes") and creds.granted_scopes:
        gs = creds.granted_scopes
        if isinstance(gs, str):
            scopes_found.update(gs.split())
        elif isinstance(gs, (list, tuple, set)):
            for item in gs:
                if isinstance(item, str):
                    scopes_found.update(item.split())

    # 3. Se token.json existir no disco e possuir o campo customizado 'granted_scopes'
    if not scopes_found and os.path.exists(TOKEN_PATH):
        try:
            import json
            with open(TOKEN_PATH, "r", encoding="utf-8") as f:
                disk_data = json.load(f)
                if "granted_scopes" in disk_data:
                    disk_scopes = disk_data["granted_scopes"]
                    if isinstance(disk_scopes, str):
                        scopes_found.update(disk_scopes.split())
                    elif isinstance(disk_scopes, (list, tuple, set)):
                        for item in disk_scopes:
                            if isinstance(item, str):
                                scopes_found.update(item.split())
        except Exception:
            pass

    # 4. Fallback: Se ainda não identificou e o creds possui access_token, consulta o endpoint tokeninfo oficial do Google
    if not scopes_found and creds and getattr(creds, "token", None):
        try:
            import urllib.request
            import json
            url = f"https://oauth2.googleapis.com/tokeninfo?access_token={creds.token}"
            req = urllib.request.Request(url, headers={"User-Agent": "FormGenerator/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                raw_scope = data.get("scope", "")
                if isinstance(raw_scope, str):
                    scopes_found.update(raw_scope.split())
                elif isinstance(raw_scope, (list, tuple, set)):
                    scopes_found.update(raw_scope)
        except Exception:
            pass

    return scopes_found


def check_required_permissions(creds, session_token=None) -> tuple[bool, list[str]]:
    """
    Verifica se o usuário concedeu os escopos essenciais (Google Drive e Formulários).
    Retorna (sucesso, lista_de_permissoes_faltantes).
    """
    granted = get_actual_granted_scopes(creds, session_token)
    
    missing = []
    has_drive = any("drive" in s.lower() for s in granted)
    has_forms = any("forms" in s.lower() for s in granted)

    if not has_drive:
        missing.append("Google Drive")
    if not has_forms:
        missing.append("Google Formulários")

    return (len(missing) == 0, missing)


def authenticate(timeout_seconds=120):
    global _active_server, _login_cancelled

    creds = None

    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(
                TOKEN_PATH,
                SCOPES
            )
            # Se o token já existe no disco, valida se ele possui as permissões necessárias
            if creds and creds.valid:
                ok, missing = check_required_permissions(creds)
                if not ok:
                    try:
                        os.remove(TOKEN_PATH)
                    except Exception:
                        pass
                    creds = None
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                ok, missing = check_required_permissions(creds)
                if not ok:
                    if os.path.exists(TOKEN_PATH):
                        try:
                            os.remove(TOKEN_PATH)
                        except Exception:
                            pass
                    creds = None
                else:
                    granted = get_actual_granted_scopes(creds)
                    save_token(creds, granted)
            except Exception:
                # Se o refresh falhar (token revogado/inválido), limpa o arquivo para novo login
                if os.path.exists(TOKEN_PATH):
                    try:
                        os.remove(TOKEN_PATH)
                    except Exception:
                        pass
                creds = None

        if not creds or not creds.valid:
            if not os.path.exists(CLIENT_SECRET_PATH):
                raise FileNotFoundError(
                    f"Arquivo de credenciais ('client_secret.json') não encontrado em:\n{CLIENT_SECRET_PATH}"
                )

            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_PATH,
                SCOPES
            )

            import wsgiref.simple_server
            original_make_server = wsgiref.simple_server.make_server

            def custom_make_server(*args, **kwargs):
                server = original_make_server(*args, **kwargs)
                global _active_server
                _active_server = server
                return server

            wsgiref.simple_server.make_server = custom_make_server
            _login_cancelled = False
            session_token = None
            try:
                # prompt='consent' garante que o Google sempre mostre as caixinhas de permissões,
                # permitindo marcar caso o usuário tenha esquecido na tentativa anterior
                creds = flow.run_local_server(
                    port=0,
                    timeout_seconds=timeout_seconds,
                    prompt="consent"
                )
                session_token = getattr(flow.oauth2session, "token", None)
            except Exception as e:
                if _login_cancelled:
                    raise RuntimeError("Login cancelado pelo usuário.") from e
                raise e
            finally:
                wsgiref.simple_server.make_server = original_make_server
                _active_server = None

            # Validação imediata pós-login: verifica se o usuário marcou as caixas de permissão essenciais
            ok, missing = check_required_permissions(creds, session_token)
            if not ok:
                # Não salva token incompleto no disco para não viciar tentativas futuras
                if os.path.exists(TOKEN_PATH):
                    try:
                        os.remove(TOKEN_PATH)
                    except Exception:
                        pass
                raise InsufficientPermissionsError(missing)

            granted = get_actual_granted_scopes(creds, session_token)
            save_token(creds, granted)

    return creds


def cancel_login():
    global _active_server, _login_cancelled
    _login_cancelled = True
    if _active_server is not None:
        try:
            _active_server.server_close()
        except Exception:
            pass


def try_auto_login():
    if not os.path.exists(TOKEN_PATH):
        return None

    try:
        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH,
            SCOPES
        )

        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                granted = get_actual_granted_scopes(creds)
                save_token(creds, granted)
            else:
                return None

        # Valida se o token gravado possui os escopos mínimos necessários
        ok, _ = check_required_permissions(creds)
        if not ok:
            if os.path.exists(TOKEN_PATH):
                try:
                    os.remove(TOKEN_PATH)
                except Exception:
                    pass
            return None

        return creds
    except Exception:
        # Se o token estiver corrompido ou revogado, remove silenciosamente
        try:
            if os.path.exists(TOKEN_PATH):
                os.remove(TOKEN_PATH)
        except Exception:
            pass
        return None


def get_user_info(creds):

    service = build(
        "oauth2",
        "v2",
        credentials=creds
    )

    info = service.userinfo().get().execute()

    return {
        "name": info.get("name"),
        "email": info.get("email")
    }


def logout_service():
    """Remove o arquivo contendo o token de autenticação local."""
    if os.path.exists(TOKEN_PATH):
        os.remove(TOKEN_PATH)


