import tkinter as tk
from tkinter import ttk
from tksheet import Sheet


class VisualizationArea(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Aba inicial
        initial_tab = ttk.Frame(self.notebook)
        self.notebook.add(initial_tab, text="Início")

        ttk.Label(
            initial_tab,
            text="Bem-vindo ao Analisador MDS",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=20)

    def show_dataframe(self, df, title="Dados"):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=title)
        self.notebook.select(tab)

        sheet = Sheet(
            tab,
            data=df.values.tolist(),
            headers=list(df.columns),
            show_x_scrollbar=True,
            show_y_scrollbar=True
        )
        sheet.pack(fill="both", expand=True)
        sheet.enable_bindings("all")
