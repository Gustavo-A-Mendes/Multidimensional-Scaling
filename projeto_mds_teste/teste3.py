import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import numpy as np
from tksheet import Sheet


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Analisador CSV - Interface")
        self.geometry("1100x600")

        # Variáveis internas
        self.matrizes = []        # lista de DataFrames
        self.matriz_atual = 0     # índice da matriz exibida

        # ============================================
        # PANED WINDOW (menu lateral + visualização)
        # ============================================
        self.paned = tk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True)

        # ===== MENU LATERAL =====
        self.frame_menu = ttk.Frame(self.paned, width=260)
        self.paned.add(self.frame_menu)
        self.paned.paneconfigure(self.frame_menu, minsize=200)

        # ===== ÁREA DE VISUALIZAÇÃO =====
        self.frame_view = ttk.Frame(self.paned)
        self.paned.add(self.frame_view)
        self.paned.paneconfigure(self.frame_view, minsize=400)

        self.create_menu()
        self.create_view_table()

    # ================================================================
    # MENU LATERAL
    # ================================================================
    def create_menu(self):
        pad = {'padx': 10, 'pady': 6}

        ttk.Label(self.frame_menu, text="CONTROLE", font=("Segoe UI", 12, "bold")).pack(pady=10)

        # Botão de importar CSV
        ttk.Button(self.frame_menu, text="Importar CSV", command=self.import_csv).pack(
            fill="x", **pad)

        ttk.Separator(self.frame_menu).pack(fill="x", pady=10)

        # Combobox para seleção de matrizes
        ttk.Label(self.frame_menu, text="Selecionar matriz:").pack(**pad)
        self.combo_matrizes = ttk.Combobox(self.frame_menu, state="readonly")
        self.combo_matrizes.pack(fill="x", **pad)
        self.combo_matrizes.bind("<<ComboboxSelected>>", lambda e: self.exibir_matriz())

        # Navegação
        nav_frame = ttk.Frame(self.frame_menu)
        nav_frame.pack(pady=10)

        ttk.Button(nav_frame, text="◀", width=5, command=self.matriz_anterior).grid(row=0, column=0, padx=5)
        ttk.Button(nav_frame, text="▶", width=5, command=self.matriz_proxima).grid(row=0, column=1, padx=5)

        ttk.Separator(self.frame_menu).pack(fill="x", pady=10)

        # Informação da matriz
        ttk.Label(self.frame_menu, text="Informações da matriz:", font=("Segoe UI", 10, "bold")).pack(**pad)

        self.label_nome = ttk.Label(self.frame_menu, text="Nome: -")
        self.label_nome.pack(**pad)

        self.label_grupo = ttk.Label(self.frame_menu, text="Grupo: -")
        self.label_grupo.pack(**pad)

        self.label_nivel = ttk.Label(self.frame_menu, text="Nível: -")
        self.label_nivel.pack(**pad)

    # ================================================================
    # ÁREA DE VISUALIZAÇÃO
    # ================================================================
    def create_view_table(self):

        ttk.Label(
            self.frame_view,
            text="Visualização da Matriz",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=10)

        # Frame que vai conter o tksheet:
        self.table_frame = ttk.Frame(self.frame_view)
        self.table_frame.pack(fill="both", expand=True)

        # Criar o widget Sheet:
        self.sheet = Sheet(
            self.table_frame,
            data=[],
            headers=[],
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            show_top_left=True
        )

        # Expandir como Sheet:
        self.sheet.pack(fill="both", expand=True)

        # Configuração inicial opcional
        self.sheet.enable_bindings(
            "single_select",  # seleção simples
            "row_select",  # pode clicar na linha inteira
            "column_select",
            "drag_select",
            "arrowkeys",
            "row_height_resize",
            # "row_width_  resize",
            "column_width_resize",
            # "column_height_resize",
            "double_click_column_resize",
            "double_click_row_resize",
            # "right_click_popup_menu",
            "rc_select",
            # "rc_insert_row",
            # "rc_delete_row",
            # "copy",
            # "paste",
            # "delete"
        )

        # # Scrollbars
        # scrollbar_y = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        # scrollbar_y.pack(side="right", fill="y")
        #
        # scrollbar_x = ttk.Scrollbar(self.frame_view, orient="horizontal", command=self.tree.xview)
        # scrollbar_x.pack(fill="x")
        #
        # self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

    # ================================================================
    # IMPORTAR CSV
    # ================================================================
    def import_csv(self):
        file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])

        if not file:
            return

        try:
            df = pd.read_csv(file)
            # Supondo que o CSV contém várias matrizes empilhadas,
            # e você já sabe como separá-las:
            self.matrizes = self.separar_matrizes(df)

            if not self.matrizes:
                messagebox.showerror("Erro", "Nenhuma matriz válida encontrada.")
                return

            # Atualizar combobox
            nomes = [f"Matriz {i+1}" for i in range(len(self.matrizes))]
            self.combo_matrizes["values"] = nomes
            self.combo_matrizes.current(0)
            self.matriz_atual = 0

            self.exibir_matriz()

        except Exception as e:
            messagebox.showerror("Erro ao importar CSV", str(e))

    # ================================================================
    # SEPARAR MATRIZES (placeholder simples)
    # ================================================================
    def separar_matrizes(self, df):
        """Carrega o CSV em um DataFrame temporário"""
        self.df = df

        termos = []
        colunas_validas = []

        for col in df.columns:
            print(col)
            # salvando dados pessoais:
            if "Nome" in col:
                print("nome: ")
                self.nomes = df[col].tolist()
                print(self.nomes)

            if "grupo" in col:
                self.grupos = df[col].tolist()

            if "nível" in col:
                self.niveis = df[col].tolist()

            # continuando...

            if "-" not in col:
                continue

            trecho = col.split("-")[1].strip()

            if " e " not in trecho:
                continue

            a, b = [x.strip() for x in trecho.split(" e ")]
            if a not in termos:
                termos.append(a)
            if b not in termos:
                termos.append(b)

            colunas_validas.append(col)

        matrizes = []

        for idx, row in df.iterrows():

            # DataFrame quadrado vazio (index = nome das linhas)
            mat = pd.DataFrame(0, index=termos, columns=termos, dtype=float)

            for col in colunas_validas:
                trecho = col.split("-")[1].strip()
                a, b = [x.strip() for x in trecho.split(" e ")]
                valor = row[col]
                mat.at[a, b] = int(valor)
                mat.at[b, a] = int(valor)

            matrizes.append(mat)

        self.treeview_header = termos

        return matrizes

    # ================================================================
    # EXIBIR MATRIZ NA TABELA
    # ================================================================
    def exibir_matriz(self):
        if not self.matrizes:
            return

        curr = self.combo_matrizes.current()
        df = self.matrizes[curr]

        # -----------------------------
        # LIMPAR TABELA ATUAL DO TKSHEET
        # -----------------------------
        self.sheet.set_sheet_data([])       # limpa dados
        self.sheet.headers([])              # limpa cabeçalho
        self.sheet.row_index([])            # limpa índice das linhas

        # -----------------------------
        # DEFINIR NOVOS HEADERS
        # -----------------------------
        headers = list(df.columns)
        self.sheet.headers(headers)

        # -----------------------------
        # DEFINIR NOMES DAS LINHAS
        # -----------------------------
        row_index = list(df.index.astype(str))
        self.sheet.row_index(row_index)

        # -----------------------------
        # INSERIR OS DADOS DO DATAFRAME
        # -----------------------------
        dados = df.values.tolist()
        self.sheet.set_sheet_data(dados)

        # -----------------------------
        # APLICAR CORES ALTERNADAS
        # -----------------------------
        for i in range(len(dados)):
            cor = "#f0f0f0" if i % 2 == 0 else "#ffffff"

            self.sheet.highlight_rows(
                rows=i,
                bg=cor,
                fg="black"
            )

        # -----------------------------
        # AJUSTE DE APARÊNCIA
        # -----------------------------
        largura = 40
        self.sheet.set_options(
            header_bg="#d9d9d9",
            header_fg="black",
            index_bg="#d9d9d9",
            index_fg="black",
            # row_height=largura,
            # column_width=largura,
            show_empty_rows=False,
        )

        self.sheet.set_all_column_widths(largura)
        self.sheet.set_all_row_heights(largura)

        # -----------------------------
        # ATUALIZAR LABELS
        # -----------------------------
        print(self.nomes[curr], self.grupos[curr], self.niveis[curr])

        self.label_nome.config(text=f"Nome: {self.nomes[curr]}")
        self.label_grupo.config(text=f"Grupo: {self.grupos[curr]}")
        self.label_nivel.config(text=f"Nível: {self.niveis[curr]}")

        # Redesenhar a tabela
        self.sheet.refresh()

    # ================================================================
    # NAVEGAÇÃO
    # ================================================================
    def matriz_anterior(self):
        if not self.matrizes:
            return
        if self.matriz_atual > 0:
            self.matriz_atual -= 1
            self.combo_matrizes.current(self.matriz_atual)
            self.exibir_matriz()

    def matriz_proxima(self):
        if not self.matrizes:
            return
        if self.matriz_atual < len(self.matrizes) - 1:
            self.matriz_atual += 1
            self.combo_matrizes.current(self.matriz_atual)
            self.exibir_matriz()


# ================================================================
# EXECUTAR
# ================================================================
if __name__ == "__main__":
    App().mainloop()
