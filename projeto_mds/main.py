import tkinter as tk
import customtkinter as ctk
from tkinter import ttk, messagebox

class MDSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MDS Analyzer")
        self.df = None  # Dataframe que será carregado

        # Botão de importa dados:
        self.btn_loadCSV = ctk.CTkButton(root, text="Carregar Arquivo CSV", command=self.load_csv)
        self.btn_loadCSV.pack(pady=10)

        # Botão de adicionar novos dados:
        self.btn_newData = ctk.CTkButton(root, text="Inserir novos dados", command=self.add_new_data)
        self.btn_newData.pack(pady=10)

        # Botão de visualização de dados:
        self.btn_viewData = ctk.CTkButton(root, text="Ver Dados", command=self.view_data)
        self.btn_viewData.pack(pady=10)

        # Botão de visualização da lista do cabeçalho:
        self.btn_viewHeader = ctk.CTkButton(root, text="Visualizar Cabeçalho", command=self.view_header)
        self.btn_viewHeader.pack(pady=10)

        # Botão para iniciar a análise MDS:
        self.btn_generateMDS = ctk.CTkButton(root, text="Gerar Análise MDS", command=self.generate_mds)
        self.btn_generateMDS.pack(pady=10)

    def load_csv(self):
        pass

    def add_new_data(self):
        pass

    def view_data(self):
        pass

    def view_header(self):
        pass

    def generate_mds(self):
        pass

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = MDSApp(root)
    root.geometry("800x600")
    root.mainloop()
