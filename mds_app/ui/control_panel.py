import tkinter as tk
from tkinter import ttk, messagebox

from mds_app.data.dataset import Dataset
from mds_app.custom_widget.scrollable_frame import ScrollableFrame


class ControlPanel(ttk.Frame):
    def __init__(self, parent, dataset, on_update_view):
        super().__init__(parent)
        self.dataset = dataset
        self.on_update_view = on_update_view
        self.selected_participant = None
        self.highlight_checkbox = None
        self.highlight_values = tk.BooleanVar()
        self.combobox = None
        self.listbox = None
        self.name_var = None
        self.group_var = None
        self.level_var = None

        self.configure(width=250)

        self._create_widgets()

    def _create_widgets(self):
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True)

        content_frame = self.scroll.content

        ttk.Label(
            content_frame,
            text="Painel de Controle",
            font=("Arial", 12, "bold")
        ).pack(pady=10)

        # ttk.Label(self, text="Informações do Participante").pack(anchor="w", padx=10)
        ttk.Separator(content_frame).pack(fill="x", padx=10, pady=5)

        # participant info:
        self.info_frame = ttk.Frame(content_frame)
        self.text_var = tk.StringVar(value="")
        self.info_label = ttk.Label(self.info_frame, textvariable=self.text_var)

        self.info_frame.pack(fill="x", pady=10)

        self.refresh()

    def refresh(self):
        if not self.dataset.participants:
            self.text_var.set(value="Nenhum dado encontrado")
        else:
            self.text_var.set(value=f"{len(self.dataset.participants)} Participante(s)")
            if not self.combobox:
                self.combobox = ttk.Combobox(self.info_frame, state="readonly")
                self.combobox.pack(fill="x", padx=10, pady=10)
                self.combobox.bind("<<ComboboxSelected>>", self._on_select)

                # navegation:
                nav_frame = ttk.Frame(self.info_frame)
                nav_frame.pack(pady=10)

                ttk.Button(nav_frame, text="◀", width=5, command=self._data_nav("anterior")).grid(row=0, column=0, padx=5)
                ttk.Button(nav_frame, text="▶", width=5, command=self._data_nav("proximo")).grid(row=0, column=1, padx=5)

                ttk.Separator(self.info_frame).pack(fill="x", pady=10)

                # Informação da matriz
                ttk.Label(self.info_frame, text="Informações da matriz:", font=("Segoe UI", 10, "bold")).pack(padx=10, pady=10)

                idx = self.combobox.current()
                self.name_var = tk.StringVar(value="Nome: - ")
                self.group_var = tk.StringVar(value="Grupo: - ")
                self.level_var = tk.StringVar(value="Nível: - ")

                label_nome = ttk.Label(self.info_frame, textvariable=self.name_var)
                label_nome.pack(padx=10, pady=10)

                label_grupo = ttk.Label(self.info_frame, textvariable=self.group_var)
                label_grupo.pack(padx=10, pady=10)

                label_nivel = ttk.Label(self.info_frame, textvariable=self.level_var)
                label_nivel.pack(padx=10, pady=10)

                self.set_data(idx)

            if not self.listbox:
                self.listbox = tk.Listbox(self.info_frame, height=8)
                self.listbox.bind("<<ListboxSelect>>", self._on_select)

                ttk.Separator(self.info_frame).pack(fill="x", pady=10)
                self.listbox.pack(fill="x", padx=10)

            if not self.highlight_checkbox:
                check_var = tk.BooleanVar()
                self.highlight_checkbox = ttk.Checkbutton(
                    self.info_frame,
                    text="Destacar valores",
                    command=self._hightlight_values,
                    variable=self.highlight_values,
                    onvalue=True,
                    offvalue=False
                )

                self.highlight_checkbox.pack(fill="x", padx=10)

            self.scroll.refresh()

        self.info_label.pack(padx=10, pady=10)

        if self.combobox:
            nomes = [p["name"] for p in self.dataset.participants]
            self.combobox["values"] = nomes
            self.combobox.current(0)

        if self.listbox:
            self.listbox.delete(0, tk.END)
            for p in self.dataset.participants:
                self.listbox.insert(tk.END, p["pid"])

        if self.highlight_checkbox:
            self.highlight_values.set(False)

    def _on_select(self, event):
        idx_listbox = self.listbox.curselection()
        idx_combobox = self.combobox.current()

        idx = None
        if idx_listbox:
            idx = idx_listbox[0]
        elif idx_combobox:
            idx = idx_combobox

        if not idx:
            return

        self.combobox.current(idx)
        self.set_data(idx)

        self.selected_participant = self.dataset.participants[idx]
        headers = self.dataset.selected_headers
        self.on_update_view(self.selected_participant, headers, self.highlight_values.get())

    def _data_nav(self, move):
        def inner_function():
            idx = self.combobox.current()

            if not self.dataset or idx < 0:
                return

            if move == "anterior":
                if idx > 0:
                    idx -= 1
                    self.combobox.current(idx)

            elif move == "proximo":
                if idx < len(self.dataset.participants) - 1:
                    idx += 1
                    self.combobox.current(idx)

            self.set_data(idx)
            self.selected_participant = self.dataset.participants[idx]
            headers = self.dataset.selected_headers
            self.on_update_view(self.selected_participant, headers, self.highlight_values.get())

        return inner_function

    def _hightlight_values(self):
        idx = [self.combobox.current()]
        if not idx:
            return

        self.selected_participant = self.dataset.participants[idx[0]]
        headers = self.dataset.selected_headers
        self.on_update_view(self.selected_participant, headers, self.highlight_values.get())

    def set_data(self, idx):
        self.name_var.set(value=f"Nome: {self.dataset.participants[idx]["name"]}")
        self.group_var.set(value=f"Nome: {self.dataset.participants[idx]["group"]}")
        self.level_var.set(value=f"Nome: {self.dataset.participants[idx]["level"]}")
