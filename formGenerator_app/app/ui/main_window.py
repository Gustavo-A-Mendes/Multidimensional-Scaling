import tkinter as tk
import webbrowser
import threading

import ttkbootstrap as ttk

from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from formGenerator_app.app.services.auth_service import (
    authenticate,
    try_auto_login,
    get_user_info,
    logout_service,
    cancel_login,
    InsufficientPermissionsError
)
from formGenerator_app.app.services.forms_service import create_forms
from formGenerator_app.app.services.clipboard_service import copy


class MainWindow:

    def __init__(self):

        self.window = ttk.Window(
            title="Gerador Acadêmico Google Forms",
            themename="flatly",
            size=(700, 600)
        )

        self.creds = None
        self.pre_url = None
        self.pos_url = None

        self.build_ui()
        self.try_auto_login()

    def build_ui(self):
        title = ttk.Label(
            self.window,
            text="Assistente de Criação de Formulários",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=15)

        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Aba 1: Autenticação
        self.tab1 = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab1, text="Passo 1: Autenticação")

        self.login_label = ttk.Label(
            self.tab1,
            text="Para gerar os formulários no seu Google Drive, é necessário conectar sua conta.",
            font=("Arial", 12),
            justify="center",
            anchor="center"
        )
        self.login_label.pack(pady=20, fill="x", padx=10)

        # Ajusta a quebra de linha do texto dinamicamente se a janela for redimensionada
        self.tab1.bind(
            "<Configure>",
            lambda event: self.login_label.configure(wraplength=event.width - 40)
        )

        self.status_label = ttk.Label(
            self.tab1,
            text="Status: Conta não conectada",
            bootstyle="danger",
            font=("Arial", 12, "bold")
        )
        self.status_label.pack(pady=10)

        self.auth_widget = ttk.Frame(self.tab1)
        self.auth_widget.pack(pady=20)
        
        self.btn_login = ttk.Button(
            self.auth_widget,
            text="Fazer Login com Google",
            bootstyle="primary",
            command=self.start_login
        )
        self.btn_login.pack()

        self.btn_cancel_login = ttk.Button(
            self.auth_widget,
            text="Cancelar Login",
            bootstyle="secondary-outline",
            command=self.cancel_login_action
        )

        self.btn_logout = ttk.Button(
            self.auth_widget,
            text="Desconectar / Trocar de Conta",
            bootstyle="danger-outline",
            command=self.logout_account
        )

        # Aba 2: Configuração
        self.tab2 = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab2, text="Passo 2: Configuração", state="disabled")

        concepts_label = ttk.Label(
            self.tab2,
            text="Digite os conceitos para análise (um por linha):",
            font=("Arial", 12, "bold")
        )
        concepts_label.pack(anchor="w", pady=(0, 10))

        self.text_area = ScrolledText(
            self.tab2,
            width=70,
            height=12
        )
        self.text_area.pack(fill="both", expand=True, pady=(0, 20))

        self.btn_generate = ttk.Button(
            self.tab2,
            text="Gerar Formulários (Pré e Pós)",
            bootstyle="success",
            command=self.generate_forms
        )
        self.btn_generate.pack(pady=10)

        # Aba 3: Exportação
        self.tab3 = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.tab3, text="Passo 3: Sucesso", state="disabled")

        success_label = ttk.Label(
            self.tab3,
            text="Formulários gerados com sucesso!",
            font=("Arial", 16, "bold"),
            bootstyle="success"
        )
        success_label.pack(pady=20)

        # Cards para Pré e Pós
        cards_frame = ttk.Frame(self.tab3)
        cards_frame.pack(fill="x", pady=10)

        # Pré-teste
        pre_frame = ttk.Labelframe(cards_frame, text="Formulário Pré-aulas", padding=15)
        pre_frame.pack(fill="x", pady=10)
        
        self.lbl_pre_url = ttk.Label(pre_frame, text="URL não gerada")
        self.lbl_pre_url.pack(anchor="w", pady=(0, 10))
        
        pre_btns = ttk.Frame(pre_frame)
        pre_btns.pack(anchor="e")
        ttk.Button(pre_btns, text="Copiar Link", bootstyle="info-outline", command=lambda: self._copy_link(self.pre_url, "Pré-aulas")).pack(side="left", padx=5)
        ttk.Button(pre_btns, text="Abrir no Navegador", bootstyle="secondary-outline", command=lambda: webbrowser.open(self.pre_url) if self.pre_url else None).pack(side="left")

        # Pós-teste
        pos_frame = ttk.Labelframe(cards_frame, text="Formulário Pós-aulas", padding=15)
        pos_frame.pack(fill="x", pady=10)
        
        self.lbl_pos_url = ttk.Label(pos_frame, text="URL não gerada")
        self.lbl_pos_url.pack(anchor="w", pady=(0, 10))
        
        pos_btns = ttk.Frame(pos_frame)
        pos_btns.pack(anchor="e")
        ttk.Button(pos_btns, text="Copiar Link", bootstyle="info-outline", command=lambda: self._copy_link(self.pos_url, "Pós-aulas")).pack(side="left", padx=5)
        ttk.Button(pos_btns, text="Abrir no Navegador", bootstyle="secondary-outline", command=lambda: webbrowser.open(self.pos_url) if self.pos_url else None).pack(side="left")

    def _copy_link(self, url, name):
        if not url:
            return
        if copy(url):
            messagebox.showinfo("Link Copiado", f"Link do formulário ({name}) copiado para a área de transferência!")
        else:
            messagebox.showwarning("Aviso", "Não foi possível copiar automaticamente para a área de transferência. Selecione e copie o link manualmente.")

    def login(self):
        try:
            self.window.after(0, self._show_connecting_state)
            self.creds = authenticate()
            user = get_user_info(self.creds)

            self.window.after(0, lambda: self._on_login_success(user, is_manual=True))
        except InsufficientPermissionsError as e:
            self.window.after(0, lambda: self._on_insufficient_permissions(e))
        except FileNotFoundError as e:
            self.window.after(0, lambda: messagebox.showerror(
                "Credenciais Não Encontradas",
                f"{str(e)}\n\n"
                "Não foi possível iniciar o login porque o arquivo de credenciais da API do Google não foi localizado."
            ))
        except Exception as e:
            err_msg = str(e)
            if "cancelado pelo usuário" in err_msg:
                self.window.after(0, lambda: messagebox.showinfo(
                    "Login Cancelado",
                    "O processo de login foi cancelado pelo usuário."
                ))
            elif "timed out" in err_msg.lower() or "tempo limite" in err_msg.lower():
                self.window.after(0, lambda: messagebox.showwarning(
                    "Tempo Limite Atingido",
                    "O tempo limite para o login no navegador foi atingido (2 minutos).\nPor favor, tente novamente."
                ))
            elif "access_denied" in err_msg.lower() or "access denied" in err_msg.lower():
                self.window.after(0, lambda: messagebox.showwarning(
                    "Acesso Não Autorizado",
                    "A autorização foi recusada ou cancelada no navegador.\n\n"
                    "Caso tenha utilizado uma conta institucional (@universidade ou @empresa), "
                    "a política de segurança da sua organização pode impedir a autorização de apps externos. "
                    "Tente novamente utilizando uma conta pessoal (@gmail.com)."
                ))
            elif any(net_term in err_msg.lower() for net_term in ["failed to establish a new connection", "name or service not known", "getaddrinfo failed", "connection reset", "network is unreachable"]):
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro de Conexão",
                    "Não foi possível se conectar aos servidores do Google.\n\n"
                    "Verifique sua conexão com a internet ou se há algum antivírus/firewall bloqueando a conexão."
                ))
            else:
                self.window.after(0, lambda: messagebox.showerror(
                    "Erro de Login",
                    f"Ocorreu um erro ao fazer login:\n{err_msg}"
                ))
        finally:
            self.window.after(0, self._restore_login_state)

    def cancel_login_action(self):
        cancel_login()

    def _show_connecting_state(self):
        self.btn_login.config(state="disabled", text="Conectando...")
        self.btn_cancel_login.pack(pady=10)

    def _restore_login_state(self):
        self.btn_login.config(state="normal", text="Fazer Login com Google")
        self.btn_cancel_login.pack_forget()

    def start_login(self):
        thread = threading.Thread(target=self.login)
        thread.daemon = True
        thread.start()

    def try_auto_login(self):
        creds = try_auto_login()
        if creds:
            self.creds = creds
            user = get_user_info(creds)
            self._on_login_success(user)

    def _on_login_success(self, user, is_manual=False):
        user_name = user.get("name", "Usuário")
        user_email = user.get("email", "")
        email_str = f" ({user_email})" if user_email else ""

        self.status_label.config(
            text=f"Conectado como: {user_name}",
            bootstyle="success"
        )
        
        # Oculta o aviso, botão de login e cancelamento, e exibe o botão de logout
        self.login_label.pack_forget()
        self.btn_login.pack_forget()
        self.btn_cancel_login.pack_forget()
        self.btn_logout.pack()
        
        self.notebook.tab(self.tab2, state="normal")
        self.notebook.select(self.tab2)

        if is_manual:
            messagebox.showinfo("Login com Sucesso", f"Bem-vindo, {user_name}!\nLogin realizado com sucesso.")

    def _on_insufficient_permissions(self, exc):
        self.creds = None
        self.login_label.pack(before=self.status_label, pady=20)
        self.status_label.config(
            text="Status: Conta não conectada",
            bootstyle="danger"
        )
        self.btn_login.config(state="normal", text="Fazer Login com Google")
        self.btn_login.pack()
        self.btn_cancel_login.pack_forget()
        self.btn_logout.pack_forget()

        self.notebook.tab(self.tab2, state="disabled")
        self.notebook.tab(self.tab3, state="disabled")
        self.notebook.select(self.tab1)

        missing = getattr(exc, "missing_permissions", None) or ["Google Drive", "Google Formulários"]

        motivos = []
        if any("drive" in m.lower() for m in missing):
            motivos.append("• Google Drive: criar a pasta onde os formulários e arquivos serão organizados e salvos.")
        if any("form" in m.lower() for m in missing):
            motivos.append("• Google Formulários: gerar automaticamente os questionários (Pré e Pós-teste) com as perguntas de comparação.")

        if not motivos:
            motivos = [
                "• Google Drive: criar a pasta onde os formulários serão salvos.",
                "• Google Formulários: gerar automaticamente os questionários de avaliação."
            ]

        motivos_str = "\n".join(motivos)

        msg = (
            "Não foi possível concluir o login porque as permissões essenciais não foram autorizadas na tela do Google.\n\n"
            f"O aplicativo precisa das seguintes permissões para funcionar:\n"
            f"{motivos_str}\n\n"
            "Como resolver:\n"
            "1. Clique no botão 'Fazer Login com Google' novamente.\n"
            "2. Na janela do navegador que se abrir, selecione a sua conta.\n"
            "3. Se aparecer a tela 'O Google não verificou este app', clique em 'Avançado' e depois em 'Acessar (não seguro)'.\n"
            "4. Na tela de permissões ('O app quer acessar sua Conta do Google'), MARQUE TODAS AS CAIXINHAS de seleção do Google Drive e Google Formulários.\n"
            "5. Clique no botão 'Continuar'.\n\n"
            "Dica: Caso esteja usando um e-mail institucional (@universidade ou corporativo) e sua organização restrinja o acesso a apps externos, utilize uma conta pessoal (@gmail.com)."
        )

        messagebox.showwarning(
            "Permissões Necessárias Não Concedidas",
            msg
        )

    def logout_account(self):
        if messagebox.askyesno("Confirmar Logout", "Deseja realmente desconectar sua conta do Google?"):
            try:
                logout_service()

                self.creds = None
                self.login_label.pack(before=self.status_label, pady=20)
                self.status_label.config(
                    text="Status: Conta não conectada",
                    bootstyle="danger"
                )
                self.btn_login.config(state="normal", text="Fazer Login com Google")
                self.btn_login.pack()
                self.btn_logout.pack_forget()

                self.notebook.tab(self.tab2, state="disabled")
                self.notebook.tab(self.tab3, state="disabled")
                self.notebook.select(self.tab1)

                messagebox.showinfo("Logout", "Conta desconectada com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao deslogar: {str(e)}")

    def generate_forms(self):
        if not self.creds:
            messagebox.showwarning("Login Necessário", "Você precisa conectar uma conta Google antes de gerar os formulários.")
            return

        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Campos Vazios", "Por favor, digite os conceitos que deseja analisar (um por linha).")
            return

        # Limpar linhas e remover vazios
        raw_concepts = [line.strip() for line in text.split("\n") if line.strip()]

        # Remover conceitos duplicados preservando a ordem
        seen = set()
        concepts = []
        duplicates = []
        for c in raw_concepts:
            if c not in seen:
                seen.add(c)
                concepts.append(c)
            else:
                duplicates.append(c)

        if len(concepts) < 2:
            messagebox.showerror(
                "Conceitos Insuficientes",
                "São necessários pelo menos 2 conceitos diferentes para possibilitar a comparação par a par.\n\n"
                f"Você informou apenas {len(concepts)} conceito(s) válido(s)."
            )
            return

        total_pairs = len(concepts) * (len(concepts) - 1) // 2

        if duplicates:
            msg_dup = "Foram encontrados termos repetidos que foram unificados automaticamente:\n- " + "\n- ".join(duplicates[:5])
            if len(duplicates) > 5:
                msg_dup += f"\n... e mais {len(duplicates) - 5} termo(s)."
            messagebox.showinfo("Termos Duplicados", msg_dup)

        if total_pairs > 45:
            confirm = messagebox.askyesno(
                "Aviso de Volume",
                f"Você inseriu {len(concepts)} conceitos, o que gerará {total_pairs} perguntas de escala por formulário.\n\n"
                "Questionários com muitos pares podem ser cansativos para os respondentes.\n"
                "Deseja continuar com a geração?",
                parent=self.window
            )
            if not confirm:
                return

        self.btn_generate.config(state="disabled", text="Gerando Formulários... Aguarde")
        
        thread = threading.Thread(target=self._process_generation, args=(concepts,))
        thread.daemon = True
        thread.start()

    def _process_generation(self, concepts):
        try:
            result = create_forms(self.creds, concepts, "Análise de Similaridade")

            self.pre_url = result["pre_url"]
            self.pos_url = result["pos_url"]

            self.window.after(0, self._on_generation_success)
        except Exception as e:
            err_msg = str(e)
            
            # Tratar erros da API do Google especificamente
            from googleapiclient.errors import HttpError
            if isinstance(e, HttpError):
                status_code = e.resp.status
                if status_code == 403:
                    user_msg = (
                        "Permissão negada pela API do Google (Erro 403).\n\n"
                        "Possíveis causas:\n"
                        "1. As permissões de acesso ao Google Drive ou Google Forms não foram concedidas durante o login.\n"
                        "2. A API do Google Forms ('forms.googleapis.com') não está ativada no projeto do Google Cloud.\n"
                        "3. Caso esteja utilizando uma conta institucional, sua organização pode bloquear a criação de arquivos via aplicativos externos."
                    )
                elif status_code == 429:
                    user_msg = (
                        "Limite de requisições do Google atingido temporariamente (Erro 429).\n\n"
                        "Aguarde cerca de 2 minutos e tente gerar novamente."
                    )
                elif status_code == 401:
                    user_msg = (
                        "Sua sessão de login expirou ou foi revogada (Erro 401).\n\n"
                        "Por favor, desconecte sua conta e faça login novamente."
                    )
                else:
                    user_msg = f"Erro na API do Google (Código {status_code}):\n{e.reason or err_msg}"
            elif any(net_term in err_msg.lower() for net_term in ["failed to establish a new connection", "getaddrinfo failed", "connection reset", "timed out", "network is unreachable"]):
                user_msg = (
                    "Falha de conexão com a internet.\n\n"
                    "A conexão caiu enquanto os formulários estavam sendo criados no Google. "
                    "Verifique sua rede e tente novamente."
                )
            else:
                user_msg = f"Ocorreu um erro ao gerar os formulários:\n{err_msg}"

            self.window.after(0, lambda: messagebox.showerror("Erro na Geração", user_msg))
            self.window.after(0, lambda: self.btn_generate.config(state="normal", text="Gerar Formulários (Pré e Pós)"))

    def _on_generation_success(self):
        self.lbl_pre_url.config(text=self.pre_url)
        self.lbl_pos_url.config(text=self.pos_url)
        
        self.btn_generate.config(state="normal", text="Gerar Formulários (Pré e Pós)")
        
        self.notebook.tab(self.tab3, state="normal")
        self.notebook.select(self.tab3)
        messagebox.showinfo("Sucesso", "Formulários Pré e Pós-aulas gerados com sucesso!")

    def run(self):
        self.window.mainloop()

