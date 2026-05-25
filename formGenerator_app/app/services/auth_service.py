import os
import sys
from googleapiclient.discovery import build

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


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


def authenticate(timeout_seconds=120):
    global _active_server, _login_cancelled

    creds = None

    if os.path.exists(TOKEN_PATH):

        creds = Credentials.from_authorized_user_file(
            TOKEN_PATH,
            SCOPES
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:

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
            try:
                creds = flow.run_local_server(port=0, timeout_seconds=timeout_seconds)
            except Exception as e:
                if _login_cancelled:
                    raise RuntimeError("Login cancelado pelo usuário.") from e
                raise e
            finally:
                wsgiref.simple_server.make_server = original_make_server
                _active_server = None

        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

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

    creds = Credentials.from_authorized_user_file(
        TOKEN_PATH,
        SCOPES
    )

    if not creds.valid:

        if creds.expired and creds.refresh_token:

            creds.refresh(Request())

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        else:
            return None

    return creds


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


