import customtkinter as ctk
import tkinter as tk
# import ttkbootstrap as ttb
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from data_handler import DataHandler

class MDSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador MDS")

        self.data_handler = DataHandler()
        self.headers = []

        # Botão para carregar arquivo CSV
        self.btn_load = ctk.CTkButton(root, text="Carregar CSV", command=self.load_csv)
        self.btn_load.pack(pady=5)

        # Botão para adicionar nova linha
        self.btn_add_row = ctk.CTkButton(root, text="Adicionar Linha", command=self.add_row_form)
        self.btn_add_row.pack(pady=5)

        # Tabela para visualizar os dados
        self.tree = ttk.Treeview(root)
        self.tree.pack(expand=True, fill="both")

    def load_csv(self):
        """Carrega um arquivo CSV e pede confirmação/edição dos cabeçalhos"""
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv")]
        )
        if not file_path:
            return

        try:
            temp_df = self.data_handler.load_csv(file_path)
            self.ask_headers(temp_df)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar o arquivo:\n{e}")

    def ask_headers(self, df):
        """Exibe uma janela para o usuário revisar/editar os cabeçalhos"""
        popup = ctk.CTkToplevel(self.root)
        popup.title("Revisar Cabeçalhos")
        popup.geometry("450x450")

        # Listbox com Scrollbar
        frame_list = ctk.CTkFrame(popup)
        frame_list.pack(expand=True, fill="both", padx=10, pady=10)

        scrollbar = ctk.CTkScrollbar(frame_list)
        scrollbar.pack(side="right", fill="y")
        listbox = tk.Listbox(frame_list, yscrollcommand=scrollbar.set, selectmode="single")
        for col in df.columns:
            listbox.insert(ctk.END, col)
        listbox.pack(side="left", expand=True, fill="both")
        scrollbar.configure(command=listbox.yview)

        # Botões de ação
        frame_buttons = ctk.CTkFrame(popup)
        frame_buttons.pack(pady=5)

        btn_remove = ctk.CTkButton(frame_buttons, text="Remover", state="disabled")
        btn_edit = ctk.CTkButton(frame_buttons, text="Editar", state="disabled")
        btn_up = ctk.CTkButton(frame_buttons, text="▲ Cima", state="disabled")
        btn_down = ctk.CTkButton(frame_buttons, text="▼ Baixo", state="disabled")

        btn_remove.grid(row=0, column=0, padx=5)
        btn_edit.grid(row=0, column=1, padx=5)
        btn_up.grid(row=0, column=2, padx=5)
        btn_down.grid(row=0, column=3, padx=5)

        def on_select(event):
            """Habilita botões quando algo é selecionado"""
            if listbox.curselection():
                index = listbox.curselection()[0]
                btn_remove.configure(state="normal")
                btn_edit.configure(state="normal")
                # mover cima só habilita se não é o primeiro
                btn_up.configure(state="normal" if index > 0 else "disabled")
                # mover baixo só habilita se não é o último
                btn_down.configure(state="normal" if index < listbox.size() - 1 else "disabled")
            else:
                btn_remove.configure(state="disabled")
                btn_edit.configure(state="disabled")
                btn_up.configure(state="disabled")
                btn_down.configure(state="disabled")

        listbox.bind("<<ListboxSelect>>", on_select)

        def remove_item():
            """Remove o item selecionado"""
            if listbox.curselection():
                index = listbox.curselection()[0]
                listbox.delete(index)

        def edit_item():
            """Edita o item selecionado"""
            if listbox.curselection():
                index = listbox.curselection()[0]
                old_value = listbox.get(index)
                new_value = tk.simpledialog.askstring("Editar Cabeçalho", f"Novo valor para '{old_value}':")
                if new_value and new_value.strip():
                    listbox.delete(index)
                    listbox.insert(index, new_value.strip())
                    listbox.selection_set(index)  # mantém selecionado

        def move_up():
            """Move o item selecionado para cima"""
            if listbox.curselection():
                index = listbox.curselection()[0]
                if index > 0:
                    value = listbox.get(index)
                    listbox.delete(index)
                    listbox.insert(index - 1, value)
                    listbox.selection_set(index - 1)

        def move_down():
            """Move o item selecionado para baixo"""
            if listbox.curselection():
                index = listbox.curselection()[0]
                if index < listbox.size() - 1:
                    value = listbox.get(index)
                    listbox.delete(index)
                    listbox.insert(index + 1, value)
                    listbox.selection_set(index + 1)

        btn_remove.configure(command=remove_item)
        btn_edit.configure(command=edit_item)
        btn_up.configure(command=move_up)
        btn_down.configure(command=move_down)

        # Entrada para adicionar novo valor
        frame_add = ctk.CTkFrame(popup)
        frame_add.pack(pady=10)

        entry_new = ctk.CTkEntry(frame_add)
        entry_new.grid(row=0, column=0, padx=5)

        btn_add = ctk.CTkButton(frame_add, text="Adicionar", state="disabled")
        btn_add.grid(row=0, column=1, padx=5)

        def on_entry_change(*args):
            """Habilita botão Adicionar quando há texto"""
            if entry_new.get().strip():
                btn_add.configure(state="normal")
            else:
                btn_add.configure(state="disabled")

        entry_new.bind("<KeyRelease>", on_entry_change)

        def add_item():
            """Adiciona novo valor"""
            value = entry_new.get().strip()
            if value:
                listbox.insert(ctk.END, value)
                entry_new.delete(0, ctk.END)
                btn_add.configure(state="disabled")

        btn_add.configure(command=add_item)

        # Botão confirmar
        def confirmar():
            self.headers = list(listbox.get(0, ctk.END))
            self.data_handler.set_headers(self.headers)
            popup.destroy()
            self.show_dataframe(self.data_handler.df)

        btn_confirm = ctk.CTkButton(popup, text="Confirmar", command=confirmar)
        btn_confirm.pack(pady=10)

    def show_dataframe(self, df: pd.DataFrame):
        """Mostra o DataFrame no Treeview"""
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        # Cabeçalhos
        for col in df.columns:
            self.tree.heading(col, text=col)

        # Linhas
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def add_row_form(self):
        """Exibe formulário avançado para adicionar uma nova linha"""
        if not self.headers:
            messagebox.showwarning("Aviso", "Carregue um CSV primeiro!")
            return

        popup = ctk.CTkToplevel(self.root)
        popup.title("Adicionar Nova Linha")
        popup.geometry("600x400")

        # Criar notebook (abas)
        notebook = ttk.Notebook(popup)
        notebook.pack(expand=True, fill="both")

        # Dicionário para armazenar os campos
        entries = {}

        # --- Aba 1: Informações principais ---
        frame_info = ttk.Frame(notebook)
        notebook.add(frame_info, text="Informações")

        info_headers = [h for h in self.headers if h.lower() in ["nome", "grupo", "nivel"]]  # separa
        for i, header in enumerate(info_headers):
            ctk.CTkLabel(frame_info, text=header).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(frame_info)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[header] = entry

        # --- Aba 2: Similaridades (em grade tipo matriz) ---
        frame_sim = ttk.Frame(notebook)
        notebook.add(frame_sim, text="Similaridades")

        sim_headers = [h for h in self.headers if h not in info_headers]
        for i, header in enumerate(sim_headers):
            ctk.CTkLabel(frame_sim, text=header).grid(row=i, column=0, padx=5, pady=5, sticky="w")
            entry = ctk.CTkEntry(frame_sim, width=10)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries[header] = entry

        # --- Aba 3: Revisão ---
        frame_review = ttk.Frame(notebook)
        notebook.add(frame_review, text="Revisão")

        lbl_review = ctk.CTkLabel(frame_review, text="Preencha os dados e clique em 'Atualizar Resumo'.",
                            justify="left", anchor="w")
        lbl_review.pack(fill="both", padx=10, pady=10)

        def atualizar_resumo():
            review_text = "Resumo dos dados:\n\n"
            # Exibir perfil
            for h in info_headers:
                review_text += f"{h}: {entries[h].get()}\n"

            review_text += "\nMatriz de Similaridades:\n"
            for h in sim_headers:
                review_text += f"{h}: {entries[h].get()}\n"

            lbl_review.configure(text=review_text)

        btn_atualizar = ctk.CTkButton(frame_review, text="Atualizar Resumo", command=atualizar_resumo)
        btn_atualizar.pack(pady=5)

        # --- Botão final de salvar ---
        def salvar():
            new_data = {h: entries[h].get() for h in self.headers}
            self.data_handler.add_row(new_data)
            self.show_dataframe(self.data_handler.df)
            popup.destroy()

        btn_add = ctk.CTkButton(popup, text="Concluir e Adicionar", command=salvar)
        btn_add.pack(pady=10)