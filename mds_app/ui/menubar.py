from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import pandas as pd
from mds_app.utils.csv_loader import *
from mds_app.ui.import_dialog import ImportDialog
from mds_app.data.participant import Participant

from mds_app.ui.control_panel import ControlPanel
from mds_app.utils.csv_loader import separate_df, load_excel, load_csv, detect_file_type


class MenuBar(tk.Menu):
    def __init__(self, parent, dataset, visualization_area, on_import):
        super().__init__(parent)
        self.parent = parent
        self.dataset = dataset
        self.visualization_area = visualization_area
        self.on_import = on_import
        #
        self._create_widgets()
        # self.configure(height=100)

    # create the toolbar area:
    def _create_widgets(self):
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # submenu:
        self.file_menu = tk.Menu(self, tearoff=False)
        self.file_menu.add_command(label="Abrir", command=self.import_csv)
        # self.file_menu.add_separator()
        self.add_cascade(label="File", menu=self.file_menu)
    #     # button
    #     self.btn_import = ttk.Button(self, text="Importar Dados", command=self.import_csv)
    #     self.btn_manual = ttk.Button(self, text="Inserir Manualmente")
    #     self.btn_manage = ttk.Button(self, text="Gerenciar Dados")
    #     self.btn_mds = ttk.Button(self, text="Análise MDS")
    #
    #     # ----------------------------------------------------------------------
    #     # setting layout:
    #     # ----------------------------------------------------------------------
    #     self.btn_import.pack(side="left", padx=5)
    #     self.btn_manual.pack(side="left", padx=5)
    #     self.btn_manage.pack(side="left", padx=5)
    #     self.btn_mds.pack(side="left", padx=5)
    #
    # toolbar methods:
    def import_csv(self):
        file_path = Path(filedialog.askopenfilename(
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Arquivos Excel", "*.xlsx *.xls"),
                ("Todos os arquivos", "*.*")
            ]
        ))

        # import canceled
        if not file_path.name:
            return

        try:
            ext = file_path.suffix.lower()
            if ext == ".csv":
                df = load_csv(file_path)
            elif ext == ".xlsx" or ext == ".xls":
                df = load_excel(file_path)
            else:
                messagebox.showerror("Erro", "Tipo de arquivo não suportado")
                return

            # detects file type:
            file_type = detect_file_type(df, ext)

            participants_data, headers = separate_df(df, file_type, ext)

            self.dataset.set_participants(participants_data)

            self.dataset.set_headers(headers)

            if not headers:
                messagebox.showerror("Erro", "Nenhuma informação válida encontrada.")
                return

            def on_confirm(new_headers):
                self.dataset.set_selected_headers(new_headers)

                # show first participant
                self.visualization_area.create_dataframe(self.dataset, index=0)

                self.on_import()

            dialog = ImportDialog(self.parent, headers, on_confirm)
            self.wait_window(dialog)

        except Exception as e:
            messagebox.showerror("Erro ao importar CSV", str(e))
