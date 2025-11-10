import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class MDSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador MDS")
        self.df = None  # DataFrame que será carregado

        # Botão para carregar arquivo CSV
        self.btn_load = ctk.CTkButton(root, text="Carregar CSV", command=self.load_csv)
        self.btn_load.pack(pady=10)

        # Tabela para visualizar os dados
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both")

        # Botão para rodar análise (placeholder)
        self.btn_analyze = ctk.CTkButton(root, text="Rodar Análise MDS", command=self.run_mds)
        self.btn_analyze.pack(pady=10)

    def load_csv(self):
        """Carrega um arquivo CSV e exibe na tabela"""
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if not file_path:
            return

        try:
            self.df = pd.read_csv(file_path)
            self.show_dataframe(self.df)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar o arquivo:\n{e}")

    def show_dataframe(self, df):
        """Mostra o DataFrame no Treeview"""
        # Limpa tabela anterior
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        # Cabeçalhos
        for col in df.columns:
            self.tree.heading(col, text=col)

        # Linhas
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def run_mds(self):
        if self.df is None:
            messagebox.showwarning("Aviso", "Carregue um CSV primeiro!")
            return
        # Aqui você coloca a sua análise MDS
        messagebox.showinfo("MDS", "Análise MDS ainda não implementada.")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark") # "light" ou "system"
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = MDSApp(root)
    root.geometry("800x600")
    root.mainloop()
