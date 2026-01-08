import tkinter as tk
from tkinter import ttk


class ImportDialog(tk.Toplevel):
    def __init__(self, parent, headers, on_confirm):
        super().__init__(parent)
        self.title("Revisão de Cabeçalhos")
        self.geometry("400x400")

        self.headers = headers
        self.on_confirm = on_confirm

        self._create_widgets()

    def _create_widgets(self):
        ttk.Label(
            self,
            text="Revise os cabeçalhos importados:",
            font=("Arial", 11, "bold")
        ).pack(pady=10)

        self.entries = []

        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10)

        for h in self.headers:
            e = ttk.Entry(frame)
            e.insert(0, h)
            e.pack(fill="x", pady=2)
            self.entries.append(e)

        ttk.Button(
            self,
            text="Confirmar",
            command=self._confirm
        ).pack(pady=10)

    def _confirm(self):
        new_headers = [e.get().strip() for e in self.entries]
        self.on_confirm(new_headers)
        self.destroy()
