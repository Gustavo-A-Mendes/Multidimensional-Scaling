import requests as rq
import tkinter as tk
import customtkinter as ctk

def validar_login():
    usuario = campo_usuario.get()
    senha = campo_senha.get()

    print(usuario, senha)

    if usuario == "gustavo" and senha == "123456":
        resultado_login.configure(text="Login feito com sucesso!", text_color="green")
    else:
        resultado_login.configure(text="Login incorreto", text_color="red")


# ==========
ctk.set_appearance_mode("dark") # "dark", "light", "system"
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema de Login")
app.geometry("300x300")

# label usuário
label_usuario = ctk.CTkLabel(app, text="Usuário")
label_usuario.pack(pady=10)
# entry usuário
campo_usuario = ctk.CTkEntry(app, placeholder_text="Digite seu usuário")
campo_usuario.pack(pady=10)

# label senha
label_senha = ctk.CTkLabel(app, text="Senha")
label_senha.pack(pady=10)
# entry senha
campo_senha = ctk.CTkEntry(app, placeholder_text="Digite sua senha", show="*")
campo_senha.pack(pady=10)

# botao de validação
botao_login = ctk.CTkButton(app, text="Login", command=validar_login)
botao_login.pack(pady=10)

# campo feedback:
resultado_login = ctk.CTkLabel(app, text="")
resultado_login.pack(pady=10)

# Iniciar a aplicação
app.mainloop()