import tkinter as tk
from tkinter import ttk


class ControlPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(
            self,
            text="Painel de Controle",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        ttk.Label(self, text="Informações do Participante").pack(anchor="w", padx=10)
        ttk.Separator(self).pack(fill="x", padx=10, pady=5)
