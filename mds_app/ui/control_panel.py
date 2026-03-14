import tkinter as tk
from tkinter import ttk, messagebox

from mds_app.custom_widget.scrollable_frame import ScrollableFrame


class ControlPanel(ttk.Frame):
    def __init__(self, parent, dataset, visualization_area):
        super().__init__(parent)
        self.dataset = dataset
        self.visualization_area = visualization_area
        self.view = None
        self.selected_participant = None
        self.combobox = None
        self.listbox = None
        self.name_var = None
        self.group_var = None
        self.level_var = None

        # plot attributes:
        self.highlight_checkbox = None
        self.highlight_values = tk.BooleanVar(value=False)
        self.destaque_view_checkbox = None
        self.destaque_view_values = tk.BooleanVar(value=True)
        self.mean_view_checkbox = None
        self.mean_view_values = tk.BooleanVar(value=False)
        self.dispersion_view_checkbox = None
        self.dispersion_view_values = tk.BooleanVar(value=False)

        self.tags = [self.highlight_values, self.destaque_view_values, self.mean_view_values, self.dispersion_view_values]

        self.configure(width=250)

        self._create_widgets()

    # create the control panel area:
    def _create_widgets(self) -> None:
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
        self.data_info_frame = ttk.Frame(content_frame)
        self.text_var = tk.StringVar(value="")
        self.info_label = ttk.Label(self.data_info_frame, textvariable=self.text_var)

        # create attribute to contain mds frame:
        self.mds_info_frame = None


        self.data_info_frame.pack(fill="x", pady=10)
        self.refresh()


    # update the control panel information:
    def refresh(self) -> None:
        if not self.dataset.participants:
            self.text_var.set(value="Nenhum dado encontrado")
        elif self.view == "data":
            self.text_var.set(value=f"{len(self.dataset.participants)} Participante(s)")

            # --------------------------------------------------
            # combobox navigation:
            if not self.combobox:
                self.combobox = ttk.Combobox(self.data_info_frame, state="readonly")
                self.combobox.pack(fill="x", padx=10, pady=10)
                self.combobox.bind("<<ComboboxSelected>>", self._on_select)

                # navegation:
                nav_frame = ttk.Frame(self.data_info_frame)
                nav_frame.pack(pady=10)

                ttk.Button(nav_frame, text="◀", width=5, command=lambda: self._data_nav("anterior")).grid(row=0, column=0, padx=5)
                ttk.Button(nav_frame, text="▶", width=5, command=lambda: self._data_nav("proximo")).grid(row=0, column=1, padx=5)

                ttk.Separator(self.data_info_frame).pack(fill="x", pady=10)

                # --------------------------------------------------
                # participant info:
                ttk.Label(self.data_info_frame, text="Informações da matriz:", font=("Segoe UI", 10, "bold")).pack(padx=10, pady=10)

                idx = self.combobox.current()
                self.name_var = tk.StringVar(value="Nome: - ")
                self.group_var = tk.StringVar(value="Grupo: - ")
                self.level_var = tk.StringVar(value="Nível: - ")

                label_nome = ttk.Label(self.data_info_frame, textvariable=self.name_var)
                label_nome.pack(padx=10, pady=10)

                label_grupo = ttk.Label(self.data_info_frame, textvariable=self.group_var)
                label_grupo.pack(padx=10, pady=10)

                label_nivel = ttk.Label(self.data_info_frame, textvariable=self.level_var)
                label_nivel.pack(padx=10, pady=10)

                self.get_metadata(idx)

            # --------------------------------------------------
            # listbox navigation:
            if not self.listbox:
                self.listbox = tk.Listbox(self.data_info_frame, height=8)
                self.listbox.bind("<<ListboxSelect>>", self._on_select)

                ttk.Separator(self.data_info_frame).pack(fill="x", pady=10)
                self.listbox.pack(fill="x", padx=10)

            # --------------------------------------------------
            # plot control:

            # highlight:
            if not self.highlight_checkbox:
                self.highlight_checkbox = ttk.Checkbutton(
                    self.data_info_frame,
                    text="Destacar valores",
                    command=self._hightlight_values,
                    variable=self.highlight_values,
                    onvalue=True,
                    offvalue=False
                )
                self.highlight_checkbox.pack(fill="x", padx=10)

            # destaque view:
            if not self.destaque_view_checkbox:
                self.destaque_view_checkbox = ttk.Checkbutton(
                    self.data_info_frame,
                    text="Visualizar em Destaque",
                    command=self._destaque_view_values,
                    variable=self.destaque_view_values,
                    onvalue=True,
                    offvalue=False
                )
                self.destaque_view_checkbox.pack(fill="x", padx=10)

            # mean view:
            if not self.mean_view_checkbox:
                self.mean_view_checkbox = ttk.Checkbutton(
                    self.data_info_frame,
                    text="Visualizar Média",
                    command=self._mean_view_values,
                    variable=self.mean_view_values,
                    onvalue=True,
                    offvalue=False
                )
                self.mean_view_checkbox.pack(fill="x", padx=10)

            # dispersion view:
            if not self.dispersion_view_checkbox:
                self.dispersion_view_checkbox = ttk.Checkbutton(
                    self.data_info_frame,
                    text="Visualizar Dispersão",
                    command=self._dispersion_view_values,
                    variable=self.dispersion_view_values,
                    onvalue=True,
                    offvalue=False
                )
                self.dispersion_view_checkbox.pack(fill="x", padx=10)

            self.scroll.refresh()

            if self.combobox:
                names = [p.name for p in self.dataset.participants]
                self.combobox["values"] = names
                self.combobox.current(0)

            if self.listbox:
                self.listbox.delete(0, tk.END)
                for p in self.dataset.participants:
                    self.listbox.insert(tk.END, p.pid)

            # if self.highlight_checkbox:
            #     self.highlight_values.set(False)
            # if self.destaque_view_checkbox:
            #     self.destaque_view_values.set(True)
            # if self.mean_view_checkbox:
            #     self.mean_view_values.set(False)
            # if self.dispersion_view_checkbox:
            #     self.dispersion_view_values.set(False)

        elif self.view == "mds":
            pass

        self.info_label.pack(padx=10, pady=10)

    # update de control panel and visualization when interact with combobox or listbox:
    def _on_select(self, event: tk.Event) -> None:
        idx_listbox = self.listbox.curselection()
        idx_combobox = self.combobox.current()

        print(idx_listbox)
        print(idx_combobox)

        idx = None
        if idx_listbox:
            idx = idx_listbox[0]
        else:
            idx = idx_combobox

        print(idx)
        if idx is None:
            return

        self.combobox.current(idx)
        self.get_metadata(idx)

        self.selected_participant = self.dataset.participants[idx]
        headers = self.dataset.selected_headers
        self.visualization_area.show_matrix(self.selected_participant, headers, self.highlight_values.get())
        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx)

    # update de control panel and visualization when interact with combobox buttons:
    def _data_nav(self, move: str) -> None:
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

        self.get_metadata(idx)
        self.selected_participant = self.dataset.participants[idx]
        headers = self.dataset.selected_headers
        self.visualization_area.show_matrix(self.selected_participant, headers, self.highlight_values.get())
        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx)

    # calls highlight method of visualization area:
    def _hightlight_values(self) -> None:
        idx = [self.combobox.current()]
        if not idx:
            return

        self.selected_participant = self.dataset.participants[idx[0]]
        headers = self.dataset.selected_headers
        self.visualization_area.show_matrix(self.selected_participant, headers, self.highlight_values.get())
        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx[0])

    # calls destaque method of visualization area:
    def _destaque_view_values(self) -> None:
        idx = [self.combobox.current()]
        if not idx:
            return

        self.selected_participant = self.dataset.participants[idx[0]]
        headers = self.dataset.selected_headers

        self.visualization_area.show_matrix(self.selected_participant, headers, self.highlight_values.get())
        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx[0])

    # calls mean_view method of visualization area:
    def _mean_view_values(self) -> None:
        idx = [self.combobox.current()]
        if not idx:
            return

        self.selected_participant = self.dataset.participants[idx[0]]

        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx[0])

    # calls destaque method of visualization area:
    def _dispersion_view_values(self) -> None:
        idx = [self.combobox.current()]
        if not idx:
            return

        self.selected_participant = self.dataset.participants[idx[0]]

        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx[0])

    # get information about the participant:
    def get_metadata(self, idx) -> None:
        self.name_var.set(value=f"Nome: {self.dataset.participants[idx].name}")
        self.group_var.set(value=f"Grupo: {self.dataset.participants[idx].group}")
        self.level_var.set(value=f"Level: {self.dataset.participants[idx].familiarity_level}")
