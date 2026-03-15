import tkinter as tk
from tkinter import ttk, messagebox

from mds_app.custom_widget.scrollable_frame import ScrollableFrame

from typing import Union, TYPE_CHECKING

# if TYPE_CHECKING:
from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant
from mds_app.ui.visualization_area import VisualizationArea

class ControlPanel(ttk.Frame):
    def __init__(self, parent, dataset: Dataset, visualization_area: VisualizationArea) -> None:
        super().__init__(parent)
        self.dataset = dataset
        self.visualization_area = visualization_area

        self.selected_participant: Participant | None = None
        self.view: str | None = None

        self.combobox: ttk.Combobox | None  = None
        self.name_var: tk.StringVar | None  = None
        self.group_var: tk.StringVar | None = None
        self.level_var: tk.StringVar | None = None

        # plot attributes:
        self.highlight_checkbox: ttk.Checkbutton | None = None
        self.highlight_values = tk.BooleanVar(value=False)

        self.destaque_view_checkbox: ttk.Checkbutton | None = None
        self.destaque_view_values = tk.BooleanVar(value=True)

        self.mean_view_checkbox: ttk.Checkbutton | None = None
        self.mean_view_values = tk.BooleanVar(value=False)

        self.dispersion_view_checkbox: ttk.Checkbutton | None   = None
        self.dispersion_view_values = tk.BooleanVar(value=False)

        self.tags: list[tk.BooleanVar] = [
            self.highlight_values,
            self.destaque_view_values,
            self.mean_view_values,
            self.dispersion_view_values
        ]

        self.configure(width=250)

        self._create_widgets()

    # create the control panel area:
    def _create_widgets(self) -> None:
        self.scroll: ScrollableFrame = ScrollableFrame(self)
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
            # plot control:

            ttk.Separator(self.data_info_frame).pack(fill="x", pady=10)

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

        elif self.view == "mds":
            pass

        self.info_label.pack(padx=10, pady=10)

    # update de control panel and visualization when interact with combobox or listbox:
    def _on_select(self, event: tk.Event) -> None:
        idx: int = self.combobox.current()

        # print(idx)
        if idx is None:
            return

        self.combobox.current(idx)
        self.get_metadata(idx)

        headers: list[str] = self.dataset.selected_headers
        self.selected_participant = self.dataset.participants[idx]
        self.visualization_area.show_matrix(self.selected_participant, headers, self.highlight_values.get())
        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx)

    # update de control panel and visualization when interact with combobox buttons:
    def _data_nav(self, move: str) -> None:
        idx: int = self.combobox.current()

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

        headers = self.dataset.selected_headers
        self.selected_participant = self.dataset.participants[idx]
        self.visualization_area.show_matrix(self.selected_participant, headers, self.highlight_values.get())
        self.visualization_area.show_mds(self.dataset, self.selected_participant, self.tags, idx)

    # calls highlight method of visualization area:
    def _hightlight_values(self) -> None:
        idx = [self.combobox.current()]
        if not idx:
            return

        headers = self.dataset.selected_headers
        self.selected_participant = self.dataset.participants[idx[0]]
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
    def get_metadata(self, idx: int) -> None:
        self.name_var.set(value=f"Nome: {self.dataset.participants[idx].name}")
        self.group_var.set(value=f"Grupo: {self.dataset.participants[idx].group}")
        self.level_var.set(value=f"Level: {self.dataset.participants[idx].familiarity_level}")
