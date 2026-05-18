import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os

from mds_app.utils.export_functions import *

class ExportWindow(tk.Toplevel):
    def __init__(self, parent, app_data):
        super().__init__(parent)
        self.title("Configurar Exportação de Dados")
        # self.geometry("500x700")
        self.app_data = app_data  # Referência aos seus dados (Dataset, MDS, etc)

        self.transient(parent)  # fica "presa" à janela pai
        self.grab_set()  # bloqueia interação com outras janelas
        self.focus_set()  # foco imediato

        # Variáveis de Controle
        self.var_matrizes = tk.BooleanVar(value=True)
        self.var_coords = tk.BooleanVar(value=True)
        self.var_plot_indiv = tk.BooleanVar()
        self.var_gabarito_indiv = tk.BooleanVar()

        # Opções da Média (3.2.1 a 3.2.6)
        self.var_plot_media = tk.BooleanVar()
        self.opt_format = tk.StringVar(value="xlsx")
        self.opt_media = tk.StringVar(value="3.2.1")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._setup_ui()

    def _setup_ui(self):
        container = ttk.Frame(self, padding=10)
        container.pack(fill="both", expand=True)

        # 1 e 2. Matrizes e Coordenadas
        lf_data = ttk.LabelFrame(container, text="Dados Numéricos", padding=5)
        lf_data.pack(fill="x", pady=5)
        self.matrix_chk = ttk.Checkbutton(lf_data, text="Matrizes de Dissimilaridade", variable=self.var_matrizes, command=self._activation_opt)
        self.matrix_chk.pack(anchor="w")
        self.matrix_format1 = ttk.Radiobutton(lf_data, text="Excel (.xlsx)", value="xlsx", variable=self.opt_format)
        self.matrix_format1.pack(anchor="w", padx=20)
        self.matrix_format2 = ttk.Radiobutton(lf_data, text="CSV (.csv)", value="csv", variable=self.opt_format)
        self.matrix_format2.pack(anchor="w", padx=20)

        self.coord_chk = ttk.Checkbutton(lf_data, text="Coordenadas MDS (.xlsx)", variable=self.var_coords)
        self.coord_chk.pack(anchor="w")

        # 3.1 Plotagens Individuais
        lf_indiv = ttk.LabelFrame(container, text="Plots Individuais (Alunos)", padding=5)
        lf_indiv.pack(fill="x", pady=5)
        self.mds_plot_chk = ttk.Checkbutton(lf_indiv, text="Exportar MDS de cada aluno", variable=self.var_plot_indiv, command=self._activation_opt)
        self.mds_plot_chk.pack(anchor="w")
        self.mean_comp_chk = ttk.Checkbutton(lf_indiv, text="Incluir comparação com Gabarito", variable=self.var_gabarito_indiv, state="disabled")
        self.mean_comp_chk.pack(anchor="w", padx=20)

        # 3.2 Plotagem da Média (Rádio botões para as sub-opções)
        lf_media = ttk.LabelFrame(container, text="Plotagem da Média da Turma", padding=5)
        lf_media.pack(fill="x", pady=5)
        self.mean_plot_chk = ttk.Checkbutton(lf_media, text="Exportar MDS da Média", variable=self.var_plot_media, command=self._activation_opt)
        self.mean_plot_chk.pack(anchor="w")

        self.options_checkbox = []
        opcoes = [
            ("Simples", "3.2.1"),
            ("Com Dispersão (Pontos)", "3.2.2"),
            ("Com Dispersão + Elipse", "3.2.3"),
            ("Com Gabarito", "3.2.4"),
            ("Com Gabarito + Dispersão", "3.2.5"),
            ("Com Gabarito + Dispersão + Elipse", "3.2.6"),
        ]
        for text, value in opcoes:
            opt = ttk.Radiobutton(lf_media, text=text, value=value, variable=self.opt_media, state="disabled")
            opt.pack(anchor="w", padx=20)

            self.options_checkbox.append(opt)

        self.progress = ttk.Progressbar(lf_media, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

        self.progress_label = ttk.Label(container, text="")
        self.progress_label.pack()

        # Botão Exportar
        self.export_btn = ttk.Button(container, text="Gerar Arquivo .ZIP", command=self.processar_exportacao)
        self.export_btn.pack(pady=20)


    def _activation_opt(self):
        if self.var_matrizes.get():
            self.matrix_format1.state(["!disabled"])
            self.matrix_format2.state(["!disabled"])
        else:
            self.matrix_format1.state(["disabled"])
            self.matrix_format2.state(["disabled"])

        if self.var_plot_indiv.get():
            self.mean_comp_chk.state(["!disabled"])
        else:
            self.mean_comp_chk.state(["disabled"])

        if self.var_plot_media.get():
            for opt in self.options_checkbox:
                opt.state(["!disabled"])
        else:
            for opt in self.options_checkbox:
                opt.state(["disabled"])

    def processar_exportacao(self):
        self._set_ui_state(False)

        filename = filedialog.asksaveasfilename(defaultextension=".zip", filetypes=[("ZIP files", "*.zip")])
        if not filename:
            self._set_ui_state(True)
            return

        self.progress["value"] = 0
        self.progress_label.config(text="Iniciando exportação...")

        thread = threading.Thread(
            target=self._executar_exportacao,
            args=(filename,)
        )
        thread.start()

    def _executar_exportacao(self, filename):
        try:
            exportar_tudo_para_zip(
                filename,
                self.app_data,
                self,
                progress_callback=self._update_progress
            )

            self.after(0, lambda: messagebox.showinfo("Sucesso", "Exportação concluída!"))
            self._set_ui_state(True)
            self.after(0, self.destroy)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Erro", str(e)))
            self._set_ui_state(True)


    def _update_progress(self, valor, total, texto=None):
        def update():
            self.progress["maximum"] = total
            self.progress["value"] = valor
            if texto is not None:
                self.progress_label.config(text=texto)

        self.after(0, update)


    def _set_ui_state(self, activate=None):
        if activate is not None:
            if activate:
                self.matrix_chk.state(["!disabled"])
                self.coord_chk.state(["!disabled"])
                self.mds_plot_chk.state(["!disabled"])
                self.mean_comp_chk.state(["!disabled"])
                self.mean_plot_chk.state(["!disabled"])
                for opt in self.options_checkbox:
                    opt.state(["!disabled"])

                self.export_btn.state(["!disabled"])

            else:
                self.matrix_chk.state(["disabled"])
                self.coord_chk.state(["disabled"])
                self.mds_plot_chk.state(["disabled"])
                self.mean_comp_chk.state(["disabled"])
                self.mean_plot_chk.state(["disabled"])
                for opt in self.options_checkbox:
                    opt.state(["disabled"])

                self.export_btn.state(["disabled"])

    #
    def _on_close(self) -> None:
        self.grab_release()
        self.destroy()