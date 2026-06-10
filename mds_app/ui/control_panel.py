import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np

from mds_app.custom_widget.scrollable_frame import ScrollableFrame

from typing import Union, TYPE_CHECKING

# if TYPE_CHECKING:
from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant
from mds_app.ui.visualization_area import VisualizationArea

class ControlPanel(ttk.Frame):
    def __init__(self, parent, dataset: Dataset, visualization_area: VisualizationArea, mode: str = "group") -> None:
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
        self.legend_frame: ttk.LabelFrame | None = None
        self.dataset_mode = mode
        self.group_controls_created = False

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
        self.info_label.pack(padx=10, pady=10)

        self.group_controls_frame = ttk.Frame(self.data_info_frame)
        self.single_controls_frame = ttk.Frame(self.data_info_frame)

        self.data_info_frame.pack(fill="x", pady=10)
        self.refresh()

    def set_mode(self, mode: str) -> None:
        self.dataset_mode = mode
        if mode == "group":
            self.single_controls_frame.pack_forget()
            self.group_controls_frame.pack(fill="x", pady=5)
        else:
            self.group_controls_frame.pack_forget()
            self.single_controls_frame.pack(fill="x", pady=5)
        self.refresh()

    def refresh(self) -> None:
        if not self.dataset.participants:
            self.text_var.set(value="Nenhum dado encontrado")
            if self.dataset_mode == "group":
                self.group_controls_frame.pack(fill="x", pady=5)
                self.single_controls_frame.pack_forget()
                self._show_group_placeholder()
            else:
                self.single_controls_frame.pack(fill="x", pady=5)
                self.group_controls_frame.pack_forget()
                self._show_single_controls()
        else:
            if self.dataset_mode == "group":
                self.single_controls_frame.pack_forget()
                self.group_controls_frame.pack(fill="x", pady=5)
                self._show_group_controls()
            else:
                self.group_controls_frame.pack_forget()
                self.single_controls_frame.pack(fill="x", pady=5)
                self._show_single_controls()

        self.update_legend()

    def _show_group_placeholder(self) -> None:
        self.group_controls_created = False
        # Limpar widgets antigos do placeholder
        for child in self.group_controls_frame.winfo_children():
            child.destroy()
            
        self.radiobuttons = []
        self.phase_radiobuttons = []
        self.combobox = None

        ttk.Label(
            self.group_controls_frame, 
            text="Carregue dados do Pré-teste para iniciar.", 
            foreground="gray",
            justify="center"
        ).pack(pady=10)

        # Botão de adicionar participante desabilitado (conforme A2)
        btn_add = ttk.Button(
            self.group_controls_frame,
            text="Adicionar Aluno Manualmente",
            state="disabled"
        )
        btn_add.pack(pady=5)
        self.scroll.refresh()

    def _show_group_controls(self) -> None:
        p_len = len(self.dataset.participants.get("professors", []))
        s_len = len(self.dataset.participants.get("students", []))
        self.text_var.set(value=f"{p_len + s_len} Participante(s)\n{p_len} Professores e {s_len} Alunos")

        # Se os widgets de controle de grupo já foram criados, apenas os atualizamos
        if not self.group_controls_created or not self.radiobuttons:
            self.group_controls_created = True
            # Limpar lixo residual se houver
            for child in self.group_controls_frame.winfo_children():
                child.destroy()
                
            self.radiobuttons = []
            self.phase_radiobuttons = []
            self.combobox = None

            radio_frame = ttk.Frame(self.group_controls_frame)
            radio_frame.pack(pady=5)

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
            self.radiobuttons.extend([default_view_radio, mean_view_radio])

            ttk.Label(radio_frame, text="Modo de visualização:").pack(fill="x", anchor="w")
            default_view_radio.pack(fill="x", side="left", padx=10, pady=5)
            mean_view_radio.pack(fill="x", side="left", padx=10, pady=5)

            # phase selection
            phase_frame = ttk.Frame(self.group_controls_frame)
            phase_frame.pack(pady=5)
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

            # combobox navigation
            self.combobox = ttk.Combobox(self.group_controls_frame, state="readonly")
            self.combobox.pack(fill="x", side="top", padx=10, pady=5)
            self.combobox.bind("<<ComboboxSelected>>", self._on_select)

            # navigation buttons
            nav_frame = ttk.Frame(self.group_controls_frame)
            nav_frame.pack(pady=5)
            self.nav_buttons = []
            nav_prev = ttk.Button(nav_frame, text="◀", width=5, command=lambda: self._data_nav("anterior"))
            nav_next = ttk.Button(nav_frame, text="▶", width=5, command=lambda: self._data_nav("proximo"))
            self.nav_buttons.extend([nav_prev, nav_next])
            nav_prev.grid(row=0, column=0, padx=5)
            nav_next.grid(row=0, column=1, padx=5)

            # Add student manually button (A2)
            btn_add_student = ttk.Button(
                self.group_controls_frame,
                text="Adicionar Aluno Manualmente",
                command=self.add_student_manually
            )
            btn_add_student.pack(fill="x", padx=10, pady=5)

            ttk.Separator(self.group_controls_frame).pack(fill="x", pady=10)

            # participant metadata labels
            self.data_label = ttk.Label(self.group_controls_frame, text="Informações da matriz:", font=("Segoe UI", 10, "bold"))
            self.data_label.pack(padx=10, pady=5)

            self.name_var = tk.StringVar(value="Nome: - ")
            self.group_var = tk.StringVar(value="Grupo: - ")
            self.level_var = tk.StringVar(value="Nível: - ")

            self.name_label = ttk.Label(self.group_controls_frame, textvariable=self.name_var)
            self.name_label.pack(padx=10, pady=2)

            self.group_label = ttk.Label(self.group_controls_frame, textvariable=self.group_var)
            self.group_label.pack(padx=10, pady=2)

            self.level_label = ttk.Label(self.group_controls_frame, textvariable=self.level_var)
            self.level_label.pack(padx=10, pady=2)

        # Atualizar estados e conteúdos
        has_pos = any(p.dataframe_pos is not None for p in self.dataset.participants["professors"] + self.dataset.participants["students"])
        if has_pos:
            self.phase_radiobuttons[1].configure(state="normal")
        else:
            self.phase_radiobuttons[1].configure(state="disabled")

        phase = self.phase_var.get()
        s_names = [p.name for p in self.dataset.participants["students"] if getattr(p, f"dataframe_{phase}") is not None]
        self.filtered_indices = [i for i, p in enumerate(self.dataset.participants["students"]) if getattr(p, f"dataframe_{phase}") is not None]
        
        self.combobox["values"] = s_names
        
        # Manter seleção se viável
        if s_names:
            idx = self.combobox.current()
            if idx < 0 or idx >= len(s_names):
                idx = 0
            self.combobox.current(idx)
            self.get_metadata(self.filtered_indices[idx])
            
        self.scroll.refresh()

    def _show_single_controls(self) -> None:
        has_matrix = self.dataset.participants and len(self.dataset.participants.get("students", [])) > 0
        if has_matrix:
            num_concepts = len(self.dataset.headers)
            self.text_var.set(value=f"Matriz de Dissimilaridade\n{num_concepts} conceitos definidos.")
        else:
            self.text_var.set(value="Nenhuma matriz ativa.\nCrie uma nova ou importe um arquivo.")

        # Recriar widgets específicos se ainda não existirem
        if not self.single_controls_frame.winfo_children():
            for child in self.single_controls_frame.winfo_children():
                child.destroy()

            ttk.Label(
                self.single_controls_frame, 
                text="Ações da Matriz", 
                font=("Segoe UI", 10, "bold")
            ).pack(pady=5)

            btn_create = ttk.Button(
                self.single_controls_frame,
                text="Criar Nova Matriz",
                command=self.create_new_matrix
            )
            btn_create.pack(fill="x", padx=10, pady=4)

            btn_manage = ttk.Button(
                self.single_controls_frame,
                text="Gerenciar Conceitos",
                command=self.manage_concepts
            )
            btn_manage.pack(fill="x", padx=10, pady=4)

            btn_add_c = ttk.Button(
                self.single_controls_frame,
                text="Adicionar Conceito",
                command=self.add_concept_manually
            )
            btn_add_c.pack(fill="x", padx=10, pady=4)

            btn_remove_c = ttk.Button(
                self.single_controls_frame,
                text="Remover Conceito",
                command=self.remove_concept_manually
            )
            btn_remove_c.pack(fill="x", padx=10, pady=4)

        self.scroll.refresh()

    def add_student_manually(self) -> None:
        if not self.dataset.headers:
            messagebox.showerror("Erro", "Você deve importar o primeiro CSV de pré-teste da turma para definir os conceitos antes de adicionar alunos manualmente.", parent=self)
            return

        name = simpledialog.askstring("Adicionar Aluno", "Nome do estudante:", parent=self)
        if not name:
            return
        name = name.strip()
        if not name:
            return

        # Verificar se existe
        existing = next((p for p in self.dataset.participants["students"] if p.name == name), None)
        if existing:
            messagebox.showerror("Erro", f"O estudante '{name}' já existe.", parent=self)
            return

        from mds_app.ui.manual_input_window import ManualInputWindow

        def on_confirm_matrix(df: pd.DataFrame) -> None:
            p = Participant(
                pid=len(self.dataset.participants["students"]),
                name=name,
                group="Aluno",
                familiarity_level=" - "
            )
            p.add_dataframe(df, "pre")

            # Se outros alunos têm pós-teste, cria pós-teste vazio
            has_pos = any(s.dataframe_pos is not None for s in self.dataset.participants["students"])
            if has_pos:
                df_pos = pd.DataFrame(0.0, index=self.dataset.headers, columns=self.dataset.headers, dtype=float)
                p.add_dataframe(df_pos, "pos")

            self.dataset.add_participant(p)
            self.dataset.calc_mean()

            # Recarregar combobox
            phase = self.phase_var.get()
            s_names = [s.name for s in self.dataset.participants["students"] if getattr(s, f"dataframe_{phase}") is not None]
            self.filtered_indices = [i for i, s in enumerate(self.dataset.participants["students"]) if getattr(s, f"dataframe_{phase}") is not None]
            self.combobox["values"] = s_names
            
            idx = s_names.index(name)
            self.combobox.current(idx)
            self._on_select(None)
            self.refresh()

        dialog = ManualInputWindow(self, self.dataset.headers, on_confirm_matrix, title=f"Preencher Distâncias para {name}")
        self.wait_window(dialog)

    def create_new_matrix(self) -> None:
        num = simpledialog.askinteger("Criar Nova Matriz", "Quantidade inicial de conceitos (2 a 50):", minvalue=2, maxvalue=50, parent=self)
        if not num:
            return

        concepts = [f"Conceito {i+1}" for i in range(num)]

        from mds_app.ui.concept_manager_window import ConceptManagerWindow
        from mds_app.ui.manual_input_window import ManualInputWindow

        def on_confirm_names(new_concepts: list[str]) -> None:
            def on_confirm_matrix(df: pd.DataFrame) -> None:
                p = Participant(
                    pid=0,
                    name="Matriz Específica",
                    group="Aluno",
                    familiarity_level=" - "
                )
                p.add_dataframe(df, "pre")

                self.dataset.set_new_participants([p])
                self.dataset.set_headers(new_concepts)
                self.dataset.set_selected_headers(new_concepts)
                self.dataset.calc_mean()

                self.visualization_area.create_dataframe()
                self.visualization_area.create_mds()
                self.refresh()
                self.visualization_area.refresh()

                dialog_names.destroy()

            #
            dialog_matrix = ManualInputWindow(self, new_concepts, on_confirm_matrix, title="Preencher Matriz Única")
            self.wait_window(dialog_matrix)

        #
        dialog_names = ConceptManagerWindow(self, concepts, on_confirm_names, title="Definir Nomes dos Conceitos")
        self.wait_window(dialog_names)

    def manage_concepts(self) -> None:
        if not self.dataset.headers:
            messagebox.showwarning("Aviso", "A matriz deve ser inicializada primeiro.", parent=self)
            return

        from mds_app.ui.concept_manager_window import ConceptManagerWindow
        from mds_app.ui.manual_input_window import ManualInputWindow

        def on_confirm(new_concepts: list[str]) -> None:
            mat_confirmed = False

            def on_confirm_matrix(df: pd.DataFrame) -> None:
                nonlocal df_mat, mat_confirmed
                df_mat = df
                mat_confirmed = True
            
            p = self.dataset.participants["students"][0]
            df_mat = p.dataframe_pre.copy()
            
            old_set = set(self.dataset.headers)
            new_set = set(new_concepts)
            new_concepts_added = new_set - old_set

            if (new_set != old_set) or (len(new_concepts) != len(self.dataset.headers)):
                # redimensiona a matriz:
                df_mat = df_mat.reindex(index=new_concepts, columns=new_concepts)

                # garante que a diagonal permaneça com valor 0:
                for h in new_concepts:
                    df_mat.at[h, h] = 0.0
                
                # se houver mais conceitos, abre a janela de edição da matriz antes de salvar:
                if (len(new_concepts_added) > 0) or (len(new_concepts) > len(self.dataset.headers)):
                    dialog_matrix = ManualInputWindow(self, new_concepts, on_confirm_matrix, df_mat, title="Preencher Matriz Única")
                    self.wait_window(dialog_matrix)

                    if not mat_confirmed:
                        return

                p.dataframe_pre = df_mat
            else:
                df_mat.columns = new_concepts
                df_mat.index = new_concepts
            
            p.mds_result_pre.fit(df_mat)

            self.dataset.update_all_headers(new_concepts)
            self.dataset.calc_mean()

            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()
            self.refresh()
            self.visualization_area.refresh()

            dialog.destroy()

        dialog = ConceptManagerWindow(self, self.dataset.headers, on_confirm, title="Gerenciar Conceitos")
        self.wait_window(dialog)

    def add_concept_manually(self) -> None:
        if not self.dataset.headers:
            self.create_new_matrix()
            return

        new_name = simpledialog.askstring("Adicionar Conceito", "Nome do novo conceito:", parent=self)
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name:
            return

        if self.dataset.headers_match(new_name):
            messagebox.showerror("Erro", f"O conceito '{new_name}' já existe.", parent=self)
            return

        self.dataset.add_header(new_name)
        self.dataset.calc_mean()

        self.visualization_area.create_dataframe()
        self.visualization_area.create_mds()
        self.refresh()
        self.visualization_area.refresh()

    def remove_concept_manually(self) -> None:
        if not self.dataset.headers:
            return

        remove_win = tk.Toplevel(self)
        remove_win.title("Remover Conceito")
        remove_win.geometry("300x150")
        remove_win.transient(self)
        remove_win.grab_set()

        # Center dialog
        remove_win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - remove_win.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - remove_win.winfo_height()) // 2
        remove_win.geometry(f"+{x}+{y}")

        ttk.Label(remove_win, text="Selecione o conceito a remover:").pack(pady=10)

        concept_var = tk.StringVar()
        combo = ttk.Combobox(remove_win, textvariable=concept_var, values=self.dataset.headers, state="readonly")
        combo.pack(pady=5)
        combo.current(0)

        def do_remove():
            h = concept_var.get()
            if h:
                confirm = messagebox.askyesno(
                    "Confirmar",
                    f"Deseja realmente remover o conceito '{h}'?",
                    parent=remove_win
                )
                if confirm:
                    self.dataset.remove_header(h)
                    self.dataset.calc_mean()

                    self.visualization_area.create_dataframe()
                    self.visualization_area.create_mds()
                    self.refresh()
                    self.visualization_area.refresh()
            remove_win.destroy()

        ttk.Button(remove_win, text="Remover", command=do_remove).pack(pady=10)

    def update_legend(self) -> None:
        if hasattr(self, "legend_frame") and self.legend_frame:
            self.legend_frame.destroy()
            self.legend_frame = None

        if not self.dataset or not self.dataset.headers:
            return

        content_frame = self.scroll.content
        self.legend_frame = ttk.LabelFrame(content_frame, text="Legenda dos Conceitos", padding=10)
        self.legend_frame.pack(fill="x", padx=10, pady=10)

        for i, h in enumerate(self.dataset.headers):
            generic = self.dataset.concept_mapping.get(h, f"C{i+1}")
            
            row_frame = ttk.Frame(self.legend_frame)
            row_frame.pack(anchor="w", fill="x", pady=2)
            
            lbl_code = ttk.Label(
                row_frame,
                text=f"{generic}: ",
                font=("Segoe UI", 9, "bold"),
                foreground="#007ACC"
            )
            lbl_code.pack(side="left", anchor="nw")
            
            lbl_name = ttk.Label(
                row_frame,
                text=h,
                font=("Segoe UI", 9),
                wraplength=180,
                justify="left"
            )
            lbl_name.pack(side="left", anchor="nw", fill="x", expand=True)

        self.scroll.refresh()

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

    def get_metadata(self, idx: int) -> None:
        p_participants = self.dataset.participants["professors"]
        s_participants = self.dataset.participants["students"]
        participants = p_participants + s_participants

        self.selected_participant = s_participants[idx]

        self.name_var.set(value=f"Nome: {self.selected_participant.name}")
        self.group_var.set(value=f"Grupo: {self.selected_participant.group}")
        self.level_var.set(value=f"Nível: {self.selected_participant.familiarity_level}")
