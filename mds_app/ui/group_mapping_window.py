import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class GroupMappingWindow(tk.Toplevel):
    def __init__(self, parent, on_confirm):
        super().__init__(parent)
        self.title("Grupo não Identificado")
        self.result = {}  # Guardará {'Docente': 'professor', '': 'student'}

        self.transient(parent)  # fica "presa" à janela pai
        self.grab_set()  # bloqueia interação com outras janelas
        self.focus_set()  # foco imediato

        ttk.Label(self, text="Não foi identificado o grupo de alguns participantes.\n\nComo devemos tratá-los?").pack(padx=10, pady=10)

        frame = ttk.Frame(self)
        frame.pack(fill="x", padx=10, pady=5)

        self.var = tk.StringVar(value="student")

        ttk.Radiobutton(frame, text="Aluno", value="Aluno", variable=self.var).pack(side="left", anchor='center', padx=20)
        ttk.Radiobutton(frame, text="Professor", value="Professor", variable=self.var).pack(side="left", anchor='center', padx=20)

        ttk.Button(self, text="Confirmar", command=lambda: on_confirm(self._get_results())).pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _get_results(self) -> str:
        self.grab_release()
        self.destroy()

        return self.var.get()

    def _on_close(self) -> None:
        self.grab_release()
        self.destroy()