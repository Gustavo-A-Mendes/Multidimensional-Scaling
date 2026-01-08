import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from utils.csv_loader import load_csv
from ui.import_dialog import ImportDialog
from data.participant import Participant

from mds_app.ui.control_panel import ControlPanel


class ToolBar(ttk.Frame):
    def __init__(self, parent, dataset, visualization_area):
        super().__init__(parent)
        self.dataset = dataset
        self.visualization_area = visualization_area
        self._create_widgets()
        self.configure(height=100)

    def _create_widgets(self):
        ttk.Button(
            self,
            text="Importar Dados",
            command=self.import_csv
        ).pack(side="left", padx=5)
        ttk.Button(
            self,
            text="Inserir Manualmente"
        ).pack(side="left", padx=5)
        ttk.Button(
            self,
            text="Gerenciar Dados"
        ).pack(side="left", padx=5)
        ttk.Button(
            self,
            text="Análise MDS"
        ).pack(side="left", padx=5)

    def import_csv(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")]
        )
        if not filepath:
            return

        try:
            df = load_csv(filepath)
            headers = list(df.columns)
        except Exception as e:
            messagebox.showerror("Erro ao importar CSV", str(e))

        def on_confirm(new_headers):
            df.columns = new_headers

            if not self.dataset.headers:
                self.dataset.set_headers(new_headers)

            participant = Participant(
                pid="P1",
                group="Grupo A",
                familiarity="Média",
                dataframe=df
            )

            self.dataset.add_participant(participant)
            self.visualization_area.show_dataframe(df, title=participant.pid)

        ImportDialog(self, headers, on_confirm)
