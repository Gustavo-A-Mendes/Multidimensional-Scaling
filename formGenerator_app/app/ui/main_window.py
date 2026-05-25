import tkinter as tk
import webbrowser
import threading

import ttkbootstrap as ttk

from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from formGenerator_app.app.services.auth_service import authenticate, try_auto_login, get_user_info, logout_service, cancel_login
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
        ttk.Button(pre_btns, text="Copiar Link", bootstyle="info-outline", command=lambda: copy(self.pre_url) if self.pre_url else None).pack(side="left", padx=5)
        ttk.Button(pre_btns, text="Abrir no Navegador", bootstyle="secondary-outline", command=lambda: webbrowser.open(self.pre_url) if self.pre_url else None).pack(side="left")

        # Pós-teste
        pos_frame = ttk.Labelframe(cards_frame, text="Formulário Pós-aulas", padding=15)
        pos_frame.pack(fill="x", pady=10)
        
        self.lbl_pos_url = ttk.Label(pos_frame, text="URL não gerada")
        self.lbl_pos_url.pack(anchor="w", pady=(0, 10))
        
        pos_btns = ttk.Frame(pos_frame)
        pos_btns.pack(anchor="e")
        ttk.Button(pos_btns, text="Copiar Link", bootstyle="info-outline", command=lambda: copy(self.pos_url) if self.pos_url else None).pack(side="left", padx=5)
        ttk.Button(pos_btns, text="Abrir no Navegador", bootstyle="secondary-outline", command=lambda: webbrowser.open(self.pos_url) if self.pos_url else None).pack(side="left")


    def login(self):
        try:
            self.window.after(0, self._show_connecting_state)
            self.creds = authenticate()
            user = get_user_info(self.creds)

            self.window.after(0, lambda: self._on_login_success(user, is_manual=True))
        except Exception as e:
            err_msg = str(e)
            if "cancelado pelo usuário" in err_msg:
                self.window.after(0, lambda: messagebox.showinfo("Login Cancelado", "O processo de login foi cancelado pelo usuário."))
            elif "Timed out" in err_msg or "Tempo limite" in err_msg or "timed out" in err_msg.lower():
                self.window.after(0, lambda: messagebox.showwarning("Tempo Limite Atingido", "O tempo limite para o login no navegador foi atingido (2 minutos). Por favor, tente novamente."))
            else:
                self.window.after(0, lambda: messagebox.showerror("Erro de Login", f"Ocorreu um erro ao fazer login:\n{err_msg}"))
            
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
            messagebox.showwarning("Login necessário", "Você precisa conectar uma conta Google.")
            return

        text = self.text_area.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Erro", "Digite ao menos um conceito.")
            return

        concepts = [line.strip() for line in text.split("\n") if line.strip()]

        self.btn_generate.config(state="disabled", text="Gerando... Aguarde")
        
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
            self.window.after(0, lambda: messagebox.showerror("Erro", str(e)))
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

