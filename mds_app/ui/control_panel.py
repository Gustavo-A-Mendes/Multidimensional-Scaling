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
        self.view_mode = tk.StringVar(value="default")
        self.filtered_indices: list[int] = []

        self.radiobuttons: list[ttk.Radiobutton] = []
        self.combobox: ttk.Combobox | None  = None
        self.radio_var: tk.StringVar | None = None
        self.name_var: tk.StringVar | None  = None
        self.group_var: tk.StringVar | None = None
        self.level_var: tk.StringVar | None = None
        
        self.phase_var: tk.StringVar | None = None
        self.phase_radiobuttons: list[ttk.Radiobutton] = []

        # self.configure(width=250)

        self._create_widgets()
        
        self.visualization_area.bind("<<RankingUpdated>>", self._on_ranking_updated)

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
        self.info_label = ttk.Label(self.data_info_frame, textvariable=self.text_var, justify="center")

        # create attribute to contain mds frame:
        # self.mds_info_frame = None

        self.data_info_frame.pack(fill="x", pady=10)
        self.refresh()

    # update the control panel information:
    def refresh(self) -> None:
        if not self.dataset.participants:
            self.text_var.set(value="Nenhum dado encontrado")
        else:
            p_len = len(self.dataset.participants["professors"])
            s_len = len(self.dataset.participants["students"])
            self.text_var.set(value=f"{p_len + s_len} Participante(s)\n{p_len} Professores e {s_len} Alunos")

            # --------------------------------------------------
            if not self.radiobuttons:
                radio_frame = ttk.Frame(self.data_info_frame)
                radio_frame.pack()

                self.radio_var = tk.StringVar(value="default")
                default_view_radio = ttk.Radiobutton(
                    radio_frame,
                    text="Padrão",
                    value="default",
                    variable=self.radio_var,
                    command=self._enable_ctrl
                )

                mean_view_radio = ttk.Radiobutton(
                    radio_frame,
                    text="Média",
                    value="mean",
                    variable=self.radio_var,
                    command=self._enable_ctrl
                )
                self.radiobuttons.append(default_view_radio)
                self.radiobuttons.append(mean_view_radio)

                #
                ttk.Label(radio_frame, text="Modo de visualização:").pack(fill="x", anchor="w")
                # for r_btn in self.radiobuttons:
                # ttk.Label(radio_frame, text=r_btn[valu])
                [r_btn.pack(fill="x", side="left", padx=10, pady=10) for r_btn in self.radiobuttons]

            # --------------------------------------------------
            # phase view navigation:
            if not self.phase_radiobuttons:
                phase_frame = ttk.Frame(self.data_info_frame)
                phase_frame.pack()
                
                self.phase_var = tk.StringVar(value="pre")
                
                ttk.Label(phase_frame, text="Fase da análise:").pack(fill="x", anchor="w")
                
                pre_radio = ttk.Radiobutton(
                    phase_frame, text="Pré-teste", value="pre", variable=self.phase_var, command=self._enable_ctrl
                )
                pos_radio = ttk.Radiobutton(
                    phase_frame, text="Pós-teste", value="pos", variable=self.phase_var, command=self._enable_ctrl
                )

                
                pre_radio.pack(fill="x", side="left", padx=10, pady=5)
                pos_radio.pack(fill="x", side="left", padx=10, pady=5)
                
                self.phase_radiobuttons = [pre_radio, pos_radio]

            has_pos = any(p.dataframe_pos is not None for p in self.dataset.participants["professors"] + self.dataset.participants["students"])
            if has_pos:
                self.phase_radiobuttons[1].configure(state="normal")
            else:
                self.phase_radiobuttons[1].configure(state="disabled")

            # combobox navigation:
            if not self.combobox:
                self.combobox = ttk.Combobox(self.data_info_frame, state="readonly")
                self.combobox.pack(fill="x", side="top", padx=10, pady=10)
                self.combobox.bind("<<ComboboxSelected>>", self._on_select)

                # navegation:
                nav_frame = ttk.Frame(self.data_info_frame)
                nav_frame.pack(pady=10)

                self.nav_buttons = []
                nav_prev = ttk.Button(nav_frame, text="◀", width=5, command=lambda: self._data_nav("anterior"))
                nav_next = ttk.Button(nav_frame, text="▶", width=5, command=lambda: self._data_nav("proximo"))

                self.nav_buttons.append(nav_prev)
                self.nav_buttons.append(nav_next)

                nav_prev.grid(row=0, column=0, padx=5)
                nav_next.grid(row=0, column=1, padx=5)

                ttk.Separator(self.data_info_frame).pack(fill="x", pady=10)

                # --------------------------------------------------
                # participant info:
                self.data_label = ttk.Label(self.data_info_frame, text="Informações da matriz:", font=("Segoe UI", 10, "bold"))
                self.data_label.pack(padx=10, pady=10)

                self.name_var = tk.StringVar(value="Nome: - ")
                self.group_var = tk.StringVar(value="Grupo: - ")
                self.level_var = tk.StringVar(value="Nível: - ")

                self.name_label = ttk.Label(self.data_info_frame, textvariable=self.name_var)
                self.name_label.pack(padx=10, pady=10)

                self.group_label = ttk.Label(self.data_info_frame, textvariable=self.group_var)
                self.group_label.pack(padx=10, pady=10)

                self.level_label = ttk.Label(self.data_info_frame, textvariable=self.level_var)
                self.level_label.pack(padx=10, pady=10)

                # --------------------------------------------------
                # plot control:

                ttk.Separator(self.data_info_frame).pack(fill="x", pady=10)

            self.scroll.refresh()

            if self.radiobuttons:
                pass

            if self.combobox:
                phase = self.phase_var.get()
                s_names = [p.name for p in self.dataset.participants["students"] if getattr(p, f"dataframe_{phase}") is not None]
                self.filtered_indices = [i for i, p in enumerate(self.dataset.participants["students"]) if getattr(p, f"dataframe_{phase}") is not None]
                self.combobox["values"] = s_names
                if s_names:
                    self.combobox.current(0)
                    self.get_metadata(self.filtered_indices[0])
                    self.visualization_area.set_index(self.filtered_indices[0])

        self.info_label.pack(padx=10, pady=10)

    #
    def _enable_ctrl(self):
        status = self.radio_var.get()
        phase = self.phase_var.get()
        if status == "default":
            self.combobox.configure(state="normal")
            self.nav_buttons[0].configure(state="normal")
            self.nav_buttons[1].configure(state="normal")
            self.data_label.configure(state="normal")
            self.name_label.configure(state="normal")
            self.group_label.configure(state="normal")
            self.level_label.configure(state="normal")
        if status == "mean":
            self.combobox.configure(state="disabled")
            self.nav_buttons[0].configure(state="disabled")
            self.nav_buttons[1].configure(state="disabled")
            self.data_label.configure(state="disabled")
            self.name_label.configure(state="disabled")
            self.group_label.configure(state="disabled")
            self.level_label.configure(state="disabled")

        idx = self.combobox.current()

        if idx is None or idx < 0:
            return

        phase = self.phase_var.get()
        # Atualiza a lista da combobox para mostrar apenas os alunos que participaram desta fase
        s_names = [p.name for p in self.dataset.participants["students"] if getattr(p, f"dataframe_{phase}") is not None]
        self.filtered_indices = [i for i, p in enumerate(self.dataset.participants["students"]) if getattr(p, f"dataframe_{phase}") is not None]
        
        self.combobox["values"] = s_names
        if s_names:
            if idx >= len(s_names):
                idx = 0
            self.combobox.current(idx)
        else:
            idx = -1
            
        global_idx = self.filtered_indices[idx] if self.filtered_indices and idx >= 0 else 0

        self.view_mode.set(value=status)

        self.visualization_area.set_index(global_idx, phase, status)

    # update de control panel and visualization when interact with combobox or listbox:
    def _on_select(self, event: tk.Event) -> None:
        cb_idx = self.combobox.current()

        if cb_idx is None or cb_idx < 0 or not self.filtered_indices:
            return

        self.combobox.current(cb_idx)
        global_idx = self.filtered_indices[cb_idx]
        self.get_metadata(global_idx)

        headers: list[str] = self.dataset.selected_headers

        p_participants = self.dataset.participants["professors"]
        s_participants = self.dataset.participants["students"]
        participants = p_participants + s_participants
        self.selected_participant = s_participants[global_idx]

        phase = self.phase_var.get()
        status = self.radio_var.get()
        self.visualization_area.set_index(global_idx, phase, status)

    # update de control panel and visualization when interact with combobox buttons:
    def _data_nav(self, move: str) -> None:
        cb_idx: int = self.combobox.current()

        if not self.dataset or cb_idx < 0 or not self.filtered_indices:
            return

        if move == "anterior":
            if cb_idx > 0:
                cb_idx -= 1
                self.combobox.current(cb_idx)

        elif move == "proximo":
            if cb_idx < len(self.filtered_indices) - 1:
                cb_idx += 1
                self.combobox.current(cb_idx)

        global_idx = self.filtered_indices[cb_idx]
        self.get_metadata(global_idx)

        headers = self.dataset.selected_headers

        p_participants = self.dataset.participants["professors"]
        s_participants = self.dataset.participants["students"]
        participants = p_participants + s_participants

        self.selected_participant = s_participants[global_idx]

        phase = self.phase_var.get()
        self.visualization_area.set_index(global_idx, phase)

    def update_combobox(self, ranked_indices: list[int]) -> None:
        if not self.combobox:
            return
            
        s_names = [self.dataset.participants["students"][i].name for i in ranked_indices]
        
        self.filtered_indices = ranked_indices
        self.combobox["values"] = s_names
        
        if len(ranked_indices) > 0:
            # try to maintain the selection if possible
            if self.selected_participant and self.selected_participant.name in s_names:
                idx = s_names.index(self.selected_participant.name)
                self.combobox.current(idx)
            else:
                self.combobox.current(0)
                self._on_select(None)
        else:
            self.combobox.set("")
            self.text_var.set("Nenhum estudante no filtro.")

    def _on_ranking_updated(self, event=None) -> None:
        if hasattr(self.visualization_area, "ranked_indices"):
            self.update_combobox(self.visualization_area.ranked_indices)

    # get information about the participant:
    def get_metadata(self, idx: int) -> None:
        p_participants = self.dataset.participants["professors"]
        s_participants = self.dataset.participants["students"]
        participants = p_participants + s_participants

        self.selected_participant = s_participants[idx]

        self.name_var.set(value=f"Nome: {self.selected_participant.name}")
        self.group_var.set(value=f"Grupo: {self.selected_participant.group}")
        self.level_var.set(value=f"Nível: {self.selected_participant.familiarity_level}")
