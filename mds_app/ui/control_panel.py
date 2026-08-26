import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np

from mds_app.custom_widget.scrollable_frame import ScrollableFrame
from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant
from mds_app.ui.participant_manager_window import ParticipantManagerWindow

class ControlPanel(ttk.Frame):
    def __init__(self, parent, dataset: Dataset, visualization_area, mode: str = "group") -> None:
        super().__init__(parent)
        self.dataset = dataset
        self.visualization_area = visualization_area
        self.dataset_mode = mode
        self.main_window = None

        self.selected_participant: Participant | None = None
        self.selected_group: str = "students"

        # Variáveis globais
        self.phase_var = tk.StringVar(value="pre")
        self.radio_var = tk.StringVar(value="default")

        self._create_widgets()
        
        # Escutar atualizações de ranking
        self.visualization_area.bind("<<RankingUpdated>>", self._on_ranking_updated)


    def _create_widgets(self) -> None:
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill="both", expand=True)

        content_frame = self.scroll.content

        ttk.Label(
            content_frame,
            text="Configurações & Filtros",
            font=("Segoe UI", 12, "bold")
        ).pack(pady=(10, 5))

        ttk.Separator(content_frame).pack(fill="x", padx=5, pady=5)


        # Container principal dos modos
        self.group_controls_frame = ttk.Frame(content_frame)
        self.single_controls_frame = ttk.Frame(content_frame)

        if self.dataset_mode == "group":
            self.group_controls_frame.pack(fill="both", expand=True)
            self._create_group_layout()
        else:
            self.single_controls_frame.pack(fill="both", expand=True)
            self._create_single_layout()

        self.refresh()


    def _create_group_layout(self) -> None:
        parent = self.group_controls_frame

        self.group_text_var = tk.StringVar(value="")
        self.group_info_label = ttk.Label(parent, textvariable=self.group_text_var, justify="center")
        self.group_info_label.pack(padx=10, pady=10)
        
        # ----------------------------------------------------
        # 1. TABELA DE PARTICIPANTES (TREEVIEW)
        # ----------------------------------------------------
        tree_parent = self.group_controls_frame

        self.tree_frame = ttk.LabelFrame(tree_parent, text="Participantes", padding=8)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        tree_y_scroll = ttk.Scrollbar(self.tree_frame)
        tree_y_scroll.pack(side="right", fill="y")
        tree_x_scroll = ttk.Scrollbar(self.tree_frame, orient="horizontal")
        tree_x_scroll.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            self.tree_frame,
            columns=("Classif", "Nome", "Grupo", "Nivel", "Pos", "Stress", "Metrica"),
            show="headings",
            height=6,
            yscrollcommand=tree_y_scroll.set,
            xscrollcommand=tree_x_scroll.set
        )
        self.tree.pack(fill="both", expand=True)
        tree_y_scroll.config(command=self.tree.yview)
        tree_x_scroll.config(command=self.tree.xview)

        # Definir cabeçalhos
        self.tree.heading("Classif", text="#")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Grupo", text="Grupo")
        self.tree.heading("Nivel", text="Nível")
        self.tree.heading("Pos", text="Pós?")
        self.tree.heading("Stress", text="Stress")
        self.tree.heading("Metrica", text="-")

        # Ajustar larguras
        self.tree.column("Classif", width=40, anchor="center")
        self.tree.column("Nome", width=85, anchor="w")
        self.tree.column("Grupo", width=65, anchor="center")
        self.tree.column("Nivel", width=55, anchor="center")
        self.tree.column("Pos", width=45, anchor="center")
        self.tree.column("Stress", width=45, anchor="center")
        self.tree.column("Metrica", width=65, anchor="center")

        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        self.tree.bind("<Double-1>", self._on_tree_double_click)

        # Rolar o Treeview com a rodinha do mouse (incluindo scroll horizontal com Shift)
        def _on_tree_enter(event):
            self.tree.bind_all("<MouseWheel>", lambda e: self.tree.yview_scroll(-int(e.delta / 120), "units"))
            self.tree.bind_all("<Shift-MouseWheel>", lambda e: self.tree.xview_scroll(-3 * int(e.delta / 120), "units"))

        def _on_tree_leave(event):
            self.tree.unbind_all("<Shift-MouseWheel>")
            if hasattr(self, "scroll") and hasattr(self.scroll, "_bind_mousewheel"):
                self.scroll._bind_mousewheel(None)
            else:
                self.tree.unbind_all("<MouseWheel>")

        self.tree.bind("<Enter>", _on_tree_enter)
        self.tree.bind("<Leave>", _on_tree_leave)

        # Barra de botões sob o Treeview
        btn_toolbar = ttk.Frame(self.tree_frame)
        btn_toolbar.pack(fill="x", pady=(8, 0))

        self.btn_new = ttk.Button(btn_toolbar, text="[+] Novo", width=8, command=self.add_participant_manually)
        self.btn_new.pack(side="left", padx=2)

        self.btn_edit = ttk.Button(btn_toolbar, text="Editar", width=8, command=self.edit_participant)
        self.btn_edit.pack(side="left", padx=2)

        self.btn_delete = ttk.Button(btn_toolbar, text="Excluir", width=8, command=self.delete_participant)
        self.btn_delete.pack(side="left", padx=2)

        # ----------------------------------------------------
        # BASE CONTROLS FRAME (aqui vão os radio buttons e afins)
        # ----------------------------------------------------
        self.base_controls_frame = ttk.Frame(tree_parent)
        self.base_controls_frame.pack(fill="both", expand=True)
        
        base_parent = self.base_controls_frame

        # ----------------------------------------------------
        # 2. OPÇÕES GLOBAIS DE ANÁLISE
        # ----------------------------------------------------
        global_frame = ttk.LabelFrame(base_parent, text="Fase e Exibição", padding=10)
        global_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(global_frame, text="Fase da Análise:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        phase_sel_frame = ttk.Frame(global_frame)
        phase_sel_frame.pack(fill="x", pady=(2, 8))
        self.pre_radio = ttk.Radiobutton(
            phase_sel_frame, text="Pré-teste", value="pre", variable=self.phase_var, command=self._on_global_change
        )
        self.pre_radio.pack(side="left", padx=(0, 10))
        self.pos_radio = ttk.Radiobutton(
            phase_sel_frame, text="Pós-teste", value="pos", variable=self.phase_var, command=self._on_global_change
        )
        self.pos_radio.pack(side="left")

        ttk.Label(global_frame, text="Modo de Exibição:", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        view_sel_frame = ttk.Frame(global_frame)
        view_sel_frame.pack(fill="x", pady=(2, 0))
        self.default_radio = ttk.Radiobutton(
            view_sel_frame, text="Padrão", value="default", variable=self.radio_var, command=self._on_global_change
        )
        self.default_radio.pack(side="left", padx=(0, 10))
        self.mean_radio = ttk.Radiobutton(
            view_sel_frame, text="Média", value="mean", variable=self.radio_var, command=self._on_global_change
        )
        self.mean_radio.pack(side="left")

        # ----------------------------------------------------
        # 3. OPÇÕES DE VISUALIZAÇÃO (PLOT)
        # ----------------------------------------------------
        plot_opts_frame = ttk.LabelFrame(base_parent, text="Opções de Visualização", padding=10)
        plot_opts_frame.pack(fill="x", padx=10, pady=5)

        self.chk_destaque = ttk.Checkbutton(
            plot_opts_frame, text="Visualizar em destaque", 
            variable=self.visualization_area.destaque_view_values,
            command=self.visualization_area.show_mds
        )
        self.chk_destaque.pack(anchor="w", pady=2)

        self.chk_mean = ttk.Checkbutton(
            plot_opts_frame, text="Visualizar gabarito", 
            variable=self.visualization_area.mean_view_values,
            command=self.visualization_area.show_mds
        )
        self.chk_mean.pack(anchor="w", pady=2)

        self.chk_dispersion = ttk.Checkbutton(
            plot_opts_frame, text="Visualizar dispersão", 
            variable=self.visualization_area.dispersion_view_values,
            command=self.visualization_area.show_mds
        )
        self.chk_dispersion.pack(anchor="w", pady=2)

        self.chk_ellipse = ttk.Checkbutton(
            plot_opts_frame, text="Visualizar zona de dispersão", 
            variable=self.visualization_area.ellipse_view_values,
            command=self.visualization_area.show_mds
        )
        self.chk_ellipse.pack(anchor="w", pady=2)

        self.chk_evo = ttk.Checkbutton(
            plot_opts_frame, text="Visualizar evolução", 
            variable=self.visualization_area.evo_view_values,
            command=self.visualization_area.show_mds
        )
        self.chk_evo.pack(anchor="w", pady=2)

        # ----------------------------------------------------
        # 4. FILTRO DE ALUNOS (RANKING)
        # ----------------------------------------------------
        ranking_frame = ttk.LabelFrame(base_parent, text="Filtro de Ranking", padding=10)
        ranking_frame.pack(fill="x", padx=10, pady=5)

        self.ranking_combo = ttk.Combobox(
            ranking_frame, 
            textvariable=self.visualization_area.ranking_mode_var,
            values=["Todos os Alunos", "Top Alinhados", "Top Divergentes", "Top Evolução"],
            state="readonly"
        )
        self.ranking_combo.pack(fill="x", pady=(0, 5))
        self.ranking_combo.bind("<<ComboboxSelected>>", lambda e: self.atualizar_estado_ranking())

        spin_frame = ttk.Frame(ranking_frame)
        spin_frame.pack(fill="x")
        self.quantidade_label = ttk.Label(spin_frame, text="Quantidade (N):")
        self.quantidade_label.pack(side="left")

        self.ranking_spin = ttk.Spinbox(
            spin_frame, from_=1, to=100, width=5, 
            textvariable=self.visualization_area.ranking_n_var,
            command=self.visualization_area.show_mds
        )
        self.ranking_spin.pack(side="right")
        self.ranking_spin.bind("<Return>", lambda e: self.visualization_area.show_mds())
        self.ranking_spin.bind("<KeyRelease>", lambda e: self._on_spinbox_keyrelease())

        # ----------------------------------------------------
        # 5. FILTRO E LEGENDA DE CONCEITOS
        # ----------------------------------------------------
        self.concept_frame = ttk.LabelFrame(base_parent, text="Conceitos Ativos", padding=10)
        self.concept_frame.pack(fill="x", padx=10, pady=5)


    def _create_single_layout(self) -> None:
        parent = self.single_controls_frame

        self.single_text_var = tk.StringVar(value="")
        self.single_info_label = ttk.Label(parent, textvariable=self.single_text_var, justify="center")
        self.single_info_label.pack(padx=10, pady=10)

        ttk.Label(
            parent, 
            text="Controles da Matriz", 
            font=("Segoe UI", 10, "bold")
        ).pack(pady=10)

        btn_create = ttk.Button(
            parent,
            text="Criar Nova Matriz",
            command=self.create_new_matrix
        )
        btn_create.pack(fill="x", padx=15, pady=5)

        btn_manage = ttk.Button(
            parent,
            text="Gerenciar Conceitos",
            command=self.manage_concepts
        )
        btn_manage.pack(fill="x", padx=15, pady=5)

        self.single_legend_frame = ttk.LabelFrame(parent, text="Legenda dos Conceitos", padding=10)
        self.single_legend_frame.pack(fill="x", padx=15, pady=10)


    def refresh(self) -> None:
        has_data = self.dataset and self.dataset.participants is not None
        
        # Verificar o modo de dataset:
        if self.dataset_mode == "group":
            self.single_controls_frame.pack_forget()
            self.group_controls_frame.pack(fill="x", pady=5)

            # Mostrar controles de métricas base se houver dados:
            if has_data:
                self.base_controls_frame.pack(fill="both", expand=True)
            else:
                self.base_controls_frame.pack_forget()
        else:
            self.group_controls_frame.pack_forget()
            self.single_controls_frame.pack(fill="x", pady=5)

        # Atualizar texto informativo
        if self.dataset_mode == "group":
            has_students = self.dataset.participants and len(self.dataset.participants.get("students", [])) > 0
        
            if has_students:
                p_len = len(self.dataset.participants.get("professors", []))
                s_len = len(self.dataset.participants.get("students", []))
                self.group_text_var.set(value=f"{p_len + s_len} Participante(s)\n{p_len} Professores e {s_len} Alunos")
            else:
                self.group_text_var.set(value="Nenhum dado encontrado.\nCarregue dados do Pré-teste para iniciar.")

            # 1. Habilitar/Desabilitar botões do pós-teste se houver pós-teste ativo
            has_pos = False
            if has_data:
                has_pos = any(
                    p.dataframe_pos is not None 
                    for p in (self.dataset.participants.get("professors", []) + self.dataset.participants.get("students", []))
                )

            if has_pos:
                self.pos_radio.configure(state="normal")
            else:
                self.pos_radio.configure(state="disabled")
                if self.phase_var.get() == "pos":
                    self.phase_var.set("pre")
            
            # 2. Re-popular Treeview de participantes
            self._populate_tree()

            # 3. Atualizar estados dos botões
            total_de_linhas = len(self.tree.get_children())
            if total_de_linhas <= 0:
                self.btn_edit.configure(state="disabled")
                self.btn_delete.configure(state="disabled")
                
            selected = self.tree.selection()
            if selected:
                self.btn_edit.configure(state="normal")
                self.btn_delete.configure(state="normal")
            else:
                self.btn_edit.configure(state="disabled")
                self.btn_delete.configure(state="disabled")

            # 4. Habilitar/desabilitar checkboxes do plot conforme o status dos dados
            self._update_plot_checkbox_states()

            # 5. Habilitar/desabilitar filtros de ranking conforme o status dos dados
            self.atualizar_estado_ranking()

            # 6. Reconstruir a lista de conceitos ativos
            self._rebuild_concept_filters()

        elif self.dataset_mode == "single":
            has_matrix = self.dataset.participants and len(self.dataset.participants.get("students", [])) > 0
            if has_matrix:
                num_concepts = len(self.dataset.headers)
                self.single_text_var.set(value=f"Matriz de Dissimilaridade\n{num_concepts} conceitos definidos.")
            else:
                self.single_text_var.set(value="Nenhuma matriz encontrada.\nCrie uma nova ou importe um arquivo.")
                
            self._update_single_legend()
            
        self.scroll.refresh()


    def _populate_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.dataset or not self.dataset.participants:
            return

        phase = self.phase_var.get()

        # 1. Alunos
        students = self.dataset.participants.get("students", [])
        
        ranked_indices = []
        if hasattr(self.visualization_area, "ranked_indices") and self.visualization_area.ranked_indices is not None:
            ranked_indices = self.visualization_area.ranked_indices
        else:
            ranked_indices = list(range(len(students)))

        ranking_mode = self.visualization_area.ranking_mode_var.get() if hasattr(self.visualization_area, "ranking_mode_var") else "Todos os Alunos"

        # Atualizar o cabeçalho da coluna Metrica
        if ranking_mode in ["Top Alinhados", "Top Divergentes"]:
            self.tree.heading("Metrica", text="Distância")
        elif ranking_mode == "Top Evolução":
            self.tree.heading("Metrica", text="Evolução")
        else:
            self.tree.heading("Metrica", text="-")

        # Calcular os rankings absolutos de alinhamento e as métricas de exibição
        alignment_ranks = {}
        metric_values = {}
        
        p_centr_ref = self.dataset.centroids.get("professors") if self.dataset.centroids else None
        if hasattr(self.visualization_area, "mds_results") and self.visualization_area.mds_results is not None:
            if p_centr_ref is not None and len(self.visualization_area.mds_results) == len(students):
                distances = []
                for j in range(len(students)):
                    student_coords = self.visualization_area.mds_results[j]
                    if not np.any(np.isnan(student_coords)) and not np.any(np.isnan(p_centr_ref)):
                        if student_coords.shape == p_centr_ref.shape:
                            dist = np.sum(np.linalg.norm(student_coords - p_centr_ref, axis=1))
                            distances.append((dist, j))
                            if ranking_mode in ["Top Alinhados", "Top Divergentes"]:
                                metric_values[j] = f"{dist:.2f}"
                
                # Ordenar por menor distância (mais alinhado)
                distances.sort(key=lambda x: x[0])
                for rank_pos, (dist, original_idx) in enumerate(distances):
                    alignment_ranks[original_idx] = rank_pos + 1

        if ranking_mode == "Top Evolução" and p_centr_ref is not None:
            mds_pre = getattr(self.visualization_area, "mds_results_pre", None)
            mds_pos = getattr(self.visualization_area, "mds_results_pos", None)
            if mds_pre is not None and mds_pos is not None:
                for j in range(len(students)):
                    pre_coords = mds_pre[j]
                    pos_coords = mds_pos[j]
                    if (pre_coords.shape == p_centr_ref.shape and 
                        pos_coords.shape == p_centr_ref.shape and 
                        not np.any(np.isnan(pre_coords)) and 
                        not np.any(np.isnan(pos_coords)) and
                        not np.any(np.isnan(p_centr_ref))):
                        
                        dist_pre = np.sum(np.linalg.norm(pre_coords - p_centr_ref, axis=1))
                        dist_pos = np.sum(np.linalg.norm(pos_coords - p_centr_ref, axis=1))
                        evo = dist_pre - dist_pos
                        metric_values[j] = f"{evo:+.2f}"

        for rank_pos, idx in enumerate(ranked_indices):
            if idx >= len(students):
                continue
            p = students[idx]
            # Stress
            stress_val = "-"
            mds_res = getattr(p, f"mds_result_{phase}")
            if mds_res and mds_res.stress is not None:
                stress_val = f"{mds_res.stress:.3f}"

            has_pos = "Sim" if p.dataframe_pos is not None else "Não"
            
            # Exibe o rank absoluto apenas nos modos Top Alinhados e Top Divergentes.
            # Omitimos ("-") em Todos os Alunos e Top Evolução.
            if ranking_mode in ["Top Alinhados", "Top Divergentes"] and idx in alignment_ranks:
                classif_val = f"{alignment_ranks[idx]}º"
            else:
                classif_val = "-"

            metric_val = metric_values.get(idx, "-")

            self.tree.insert(
                "",
                "end",
                iid=f"student_{idx}",
                values=(classif_val, p.name, p.group, p.familiarity_level, has_pos, stress_val, metric_val)
            )

        # 2. Professores
        professors = self.dataset.participants.get("professors", [])
        for i, p in enumerate(professors):
            # Professores usam pós se tiverem, senão pré
            stress_val = "-"
            mds_res = p.mds_result_pos if p.dataframe_pos is not None else p.mds_result_pre
            if mds_res and mds_res.stress is not None:
                stress_val = f"{mds_res.stress:.3f}"

            has_pos = "Sim" if p.dataframe_pos is not None else "Não"
            self.tree.insert(
                "",
                "end",
                iid=f"professor_{i}",
                values=("-", p.name, p.group, p.familiarity_level, has_pos, stress_val, "-")
            )

        # Tentar re-selecionar o participante selecionado
        if self.selected_participant:
            found_iid = None
            if self.selected_group == "students":
                for i, p in enumerate(students):
                    if p.name == self.selected_participant.name:
                        found_iid = f"student_{i}"
                        break
            else:
                for i, p in enumerate(professors):
                    if p.name == self.selected_participant.name:
                        found_iid = f"professor_{i}"
                        break
            if found_iid and self.tree.exists(found_iid):
                self.tree.selection_set(found_iid)
                self.tree.see(found_iid)


    def _update_plot_checkbox_states(self) -> None:
        has_professors = self.dataset.has_professors if self.dataset else False
        has_students = self.dataset.has_students if self.dataset else False
        phase = self.phase_var.get()
        status = self.radio_var.get()

        # Destaque
        if not status == "default":
            self.visualization_area.destaque_view_values.set(False)
            self.chk_destaque.state(["alternate", "disabled"])
        else:
            self.visualization_area.destaque_view_values.set(True)
            self.chk_destaque.state(["!alternate", "!disabled"])

        # Gabarito
        if not has_professors:
            self.visualization_area.mean_view_values.set(False)
            self.chk_mean.state(["disabled"])
        else:
            self.chk_mean.state(["!disabled"])

        # Evolução
        if not has_professors or not has_students or phase == "pre":
            self.visualization_area.evo_view_values.set(False)
            self.chk_evo.state(["alternate","disabled"])
        else:
            self.chk_evo.state(["!alternate", "!disabled"])

        # Dispersão
        if not has_students:
            self.visualization_area.dispersion_view_values.set(False)
            self.visualization_area.ellipse_view_values.set(False)
            self.chk_dispersion.state(["disabled"])
            self.chk_ellipse.state(["disabled"])
        else:
            self.chk_dispersion.state(["!disabled"])
            self.chk_ellipse.state(["!disabled"])
    

    def atualizar_estado_ranking(self):
        if self.visualization_area.ranking_mode_var.get() == "Todos os Alunos":
            self.ranking_spin.state(['disabled'])
            self.quantidade_label.config(foreground="gray")
        else:
            self.ranking_spin.state(['!disabled'])
            self.quantidade_label.config(foreground="")

        self.visualization_area.show_mds()


    def _on_spinbox_keyrelease(self) -> None:
        try:
            val = self.ranking_spin.get()
            if val.isdigit():
                self.visualization_area.ranking_n_var.set(int(val))
                self.visualization_area.show_mds()
        except Exception:
            pass


    def _rebuild_concept_filters(self) -> None:
        for child in self.concept_frame.winfo_children():
            child.destroy()

        if not self.dataset or not self.dataset.headers:
            ttk.Label(self.concept_frame, text="Nenhum conceito ativo", foreground="gray").pack(pady=5)
            return

        # Checkbox "Selecionar Tudo"
        self.all_chk = ttk.Checkbutton(
            self.concept_frame,
            text="Selecionar Tudo",
            variable=self.visualization_area.all_selection_values,
            command=self._select_all_concepts
        )
        self.all_chk.pack(anchor="w", pady=(0, 5))

        # Listar cada conceito
        for i, header in enumerate(self.dataset.headers):
            generic_name = self.dataset.concept_mapping.get(header, f"C{i+1}")
            display_text = f"{generic_name}: {header}"
            
            # Limitar tamanho para não estourar o painel lateral
            if len(display_text) > 34:
                display_text = display_text[:31] + "..."

            chk = ttk.Checkbutton(
                self.concept_frame,
                text=display_text,
                variable=self.visualization_area.concept_visibility[i],
                command=self._select_concept
            )
            chk.pack(anchor="w", pady=1, padx=(10, 0))
            

    def _select_all_concepts(self) -> None:
        val = self.visualization_area.all_selection_values.get()
        if hasattr(self.visualization_area, "concept_visibility"):
            for visibility in self.visualization_area.concept_visibility:
                visibility.set(val)
        self.visualization_area.show_mds()


    def _select_concept(self) -> None:
        self.visualization_area.show_mds()

        if hasattr(self.visualization_area, "concept_visibility"):
            count_visible = np.array([v.get() for v in self.visualization_area.concept_visibility])
            
            if np.all(count_visible):
                self.all_chk.state(['!alternate'])
            elif np.all(count_visible == False):
                self.all_chk.state(['!alternate'])
            else:
                self.all_chk.state(['alternate'])
            

    def _on_global_change(self) -> None:
        status = self.radio_var.get()
        phase = self.phase_var.get()

        if status == "default":
            self.tree.configure(selectmode="browse")
            self._update_plot_checkbox_states()
        else: # status == "mean"
            self.tree.configure(selectmode="none")

        selected_items = self.tree.selection()
        idx = 0
        group = "students"
        
        if selected_items:
            item_id = selected_items[0]
            idx = int(item_id.split("_")[1])
            group = "students" if item_id.startswith("student_") else "professors"

        # Ajusta os filtros de acordo com a fase:
        if phase == "pre":
            self.ranking_combo["values"] = ["Todos os Alunos", "Top Alinhados", "Top Divergentes"]
            if self.visualization_area.ranking_mode_var.get() == "Top Evolução":
                self.visualization_area.ranking_mode_var.set("Todos os Alunos")
                self.atualizar_estado_ranking()
        if phase == "pos":
            self.ranking_combo["values"] = ["Todos os Alunos", "Top Alinhados", "Top Divergentes", "Top Evolução"]

        self.visualization_area.set_index(idx, phase, status, group=group)
        self.refresh()


    def _on_tree_select(self, event=None) -> None:
        selected_items = self.tree.selection()
        if not selected_items:
            self.selected_participant = None
            self.btn_edit.configure(state="disabled")
            self.btn_delete.configure(state="disabled")
            return

        self.btn_edit.configure(state="normal")
        self.btn_delete.configure(state="normal")

        item_id = selected_items[0]
        idx = int(item_id.split("_")[1])
        
        if item_id.startswith("student_"):
            self.selected_participant = self.dataset.participants["students"][idx]
            self.selected_group = "students"
        else:
            self.selected_participant = self.dataset.participants["professors"][idx]
            self.selected_group = "professors"

        phase = self.phase_var.get()
        status = self.radio_var.get()
        
        self.visualization_area.set_index(idx, phase, status, group=self.selected_group)


    def _on_tree_double_click(self, event=None) -> None:
        # Abrir gerenciador no participante duplo-clicado
        self.edit_participant()


    def _on_ranking_updated(self, event=None) -> None:
        # Quando a área de visualização atualiza a ordenação de alunos pelo ranking,
        # atualiza a Treeview para destacar o ranking
        if hasattr(self.visualization_area, "ranked_indices"):
            self._populate_tree()


    # ----------------------------------------------------
    # OPERAÇÕES DE CRUD (NOVO, EDITAR, EXCLUIR)
    # ----------------------------------------------------
    def add_participant_manually(self) -> None:
        if not self.dataset.headers:
            # Caso ainda não haja conceitos definidos, solicita
            num = simpledialog.askinteger(
                "Quantidade de Conceitos",
                "Quantidade inicial de conceitos (2 a 50):",
                minvalue=2,
                maxvalue=50,
                parent=self
            )
            if not num:
                return

            concepts = [f"Conceito {i+1}" for i in range(num)]
            concept_names_confirmed = False
            final_headers = []

            from mds_app.ui.concept_manager_window import ConceptManagerWindow
            def on_confirm_names(concept_mapping: list[tuple[str,str]]) -> None:
                nonlocal final_headers, concept_names_confirmed
                final_headers = [c[0] for c in concept_mapping]
                concept_names_confirmed = True
                dialog_names.destroy()

            dialog_names = ConceptManagerWindow(self, concepts, on_confirm_names, title="Definir Nomes dos Conceitos")
            self.wait_window(dialog_names)

            if not concept_names_confirmed:
                return

            self.dataset.set_headers(final_headers)
            self.dataset.set_selected_headers(final_headers)

        def on_confirm(result):
            p = Participant(
                pid=0,
                name=result["name"],
                group=result["group"],
                familiarity_level=result["familiarity_level"]
            )
            
            p.add_dataframe(result["df_pre"], "pre")
            if result["df_pos"] is not None:
                p.add_dataframe(result["df_pos"], "pos")

            self.dataset.add_participants([p])
            self.dataset.calc_mean()

            # Forçar inicialização dos plots
            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()

            self.refresh()
            self.visualization_area.refresh()
            if self.main_window and self.main_window.toolbar:
                self.main_window.toolbar.set_mode(self.main_window.current_mode)

            # Focar no novo item inserido
            tree_key = "students" if result["group"] == "Aluno" else "professors"
            new_idx = len(self.dataset.participants[tree_key]) - 1
            iid = f"student_{new_idx}" if result["group"] == "Aluno" else f"professor_{new_idx}"
            if self.tree.exists(iid):
                self.tree.selection_set(iid)

        # Abrir o novo gerenciador
        dialog = ParticipantManagerWindow(self, self.dataset, participant=None, on_confirm=on_confirm)
        self.wait_window(dialog)


    def edit_participant(self) -> None:
        if not self.selected_participant:
            return

        def on_confirm(result):
            p = self.selected_participant
            old_name = p.name
            old_group = p.group
            new_name = result["name"]
            new_group = result["group"]

            p.name = new_name
            p.familiarity_level = result["familiarity_level"]

            # Atualiza matrizes
            p.add_dataframe(result["df_pre"], "pre")
            if result["df_pos"] is not None:
                p.add_dataframe(result["df_pos"], "pos")
            else:
                p.dataframe_pos = None
                p.mds_result_pos = None

            # Caso o grupo tenha mudado (Aluno <-> Professor), move o participante
            if old_group.upper() != new_group.upper():
                p.group = new_group
                old_key = "students" if old_group.upper() == "ALUNO" else "professors"
                new_key = "students" if new_group.upper() == "ALUNO" else "professors"
                
                if p in self.dataset.participants[old_key]:
                    self.dataset.participants[old_key].remove(p)
                self.dataset.participants[new_key].append(p)

            self.dataset.calc_mean()

            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()
            self.refresh()
            self.visualization_area.refresh()
            if self.main_window and self.main_window.toolbar:
                self.main_window.toolbar.set_mode(self.main_window.current_mode)

        dialog = ParticipantManagerWindow(self, self.dataset, participant=self.selected_participant, on_confirm=on_confirm)
        self.wait_window(dialog)


    def delete_participant(self) -> None:
        if not self.selected_participant:
            return

        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Deseja realmente excluir o participante '{self.selected_participant.name}'?",
            parent=self
        )
        if not confirm:
            return

        p = self.selected_participant
        key = "students" if p.group.upper() == "ALUNO" else "professors"
        
        if p in self.dataset.participants[key]:
            self.dataset.participants[key].remove(p)

        self.dataset.calc_mean()
        self.selected_participant = None

        # Verificar se não há mais nenhum participante no dataset
        has_any = False
        if self.dataset.participants:
            has_any = any(len(self.dataset.participants[gk]) > 0 for gk in ["students", "professors"])

        if not has_any:
            if self.main_window:
                self.main_window.clear_dataset()
            else:
                self.dataset.clear()
                self.refresh()
                self.visualization_area.refresh()
        else:
            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()
            self.refresh()
            self.visualization_area.refresh()
            if self.main_window and self.main_window.toolbar:
                self.main_window.toolbar.set_mode(self.main_window.current_mode)

    # ----------------------------------------------------
    # MÉTODOS AUXILIARES DE MATRIZ ÚNICA
    # ----------------------------------------------------
    def create_new_matrix(self) -> None:
        if self.dataset and self.dataset.participants:
            confirm = messagebox.askyesno(
                "Aviso de Sobrescrita",
                "Criar uma nova matriz irá limpar todos os dados atuais do sistema.\nDeseja continuar?",
                parent=self
            )
            if not confirm:
                return

        num = simpledialog.askinteger("Criar Nova Matriz", "Quantidade inicial de conceitos (2 a 50):", minvalue=2, maxvalue=50, parent=self)
        if not num:
            return

        concepts = [f"Conceito {i+1}" for i in range(num)]

        from mds_app.ui.concept_manager_window import ConceptManagerWindow
        from mds_app.ui.manual_input_window import ManualInputWindow

        def on_confirm_names(concept_mapping: list[tuple[str,str]]) -> None:
            def on_confirm_matrix(df: pd.DataFrame) -> None:
                p = Participant(
                    pid=0,
                    name="Matriz Específica",
                    group="Aluno",
                    familiarity_level=" - "
                )
                p.add_dataframe(df, "pre")

                self.dataset.set_new_participants([p])
                self.dataset.set_headers(final_headers)
                self.dataset.set_selected_headers(final_headers)
                self.dataset.calc_mean()

                self.visualization_area.create_dataframe()
                self.visualization_area.create_mds()
                self.refresh()
                self.visualization_area.refresh()
                if self.main_window:
                    self.main_window.root.update()
                    self.main_window.main_paned.sash_place(0, 300, 0)
                    if self.main_window.toolbar:
                        self.main_window.toolbar.set_mode(self.main_window.current_mode)

                dialog_names.destroy()

            final_headers = [c[0] for c in concept_mapping]
            dialog_matrix = ManualInputWindow(self, final_headers, on_confirm_matrix, title="Preencher Matriz Única")
            self.wait_window(dialog_matrix)

        dialog_names = ConceptManagerWindow(self, concepts, on_confirm_names, title="Definir Nomes dos Conceitos")
        self.wait_window(dialog_names)


    def manage_concepts(self) -> None:
        if not self.dataset.headers:
            messagebox.showwarning("Aviso", "A matriz deve ser inicializada primeiro.", parent=self)
            return

        from mds_app.ui.concept_manager_window import ConceptManagerWindow
        from mds_app.ui.manual_input_window import ManualInputWindow

        def on_confirm(concept_mapping: list[tuple[str,str]]) -> None:
            mat_confirmed = False

            def on_confirm_matrix(df: pd.DataFrame) -> None:
                nonlocal df_mat, mat_confirmed
                df_mat = df
                mat_confirmed = True
            
            p = self.dataset.participants["students"][0]
            df_mat = p.dataframe_pre.copy()
            
            renamed_dic = {}
            final_headers = []

            for (nome_atual, nome_original) in concept_mapping:
                final_headers.append(nome_atual)
                if nome_original and nome_atual != nome_original:
                    renamed_dic[nome_original] = nome_atual
            
            if renamed_dic:
                df_mat = df_mat.rename(index=renamed_dic, columns=renamed_dic)

            df_mat = df_mat.reindex(index=final_headers, columns=final_headers, fill_value=0.0)

            for h in final_headers:
                df_mat.at[h, h] = 0.0
                
            dialog_matrix = ManualInputWindow(self, final_headers, on_confirm_matrix, df_mat, title="Preencher Matriz Única")
            self.wait_window(dialog_matrix)

            if not mat_confirmed:
                return

            p.dataframe_pre = df_mat
            p.mds_result_pre.fit(df_mat)

            self.dataset.update_all_headers(final_headers)
            self.dataset.calc_mean()

            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()
            self.refresh()
            self.visualization_area.refresh()

            dialog.destroy()

        dialog = ConceptManagerWindow(self, self.dataset.headers, on_confirm, title="Gerenciar Conceitos")
        self.wait_window(dialog)


    def _update_single_legend(self) -> None:
        for child in self.single_legend_frame.winfo_children():
            child.destroy()

        if not self.dataset or not self.dataset.headers:
            ttk.Label(self.single_legend_frame, text="Nenhuma matriz cadastrada", foreground="gray").pack(pady=5)
            return

        for i, h in enumerate(self.dataset.headers):
            generic = self.dataset.concept_mapping.get(h, f"C{i+1}")
            
            row_frame = ttk.Frame(self.single_legend_frame)
            row_frame.pack(anchor="w", fill="x", pady=2)
            
            lbl_code = ttk.Label(
                row_frame, text=f"{generic}: ",
                font=("Segoe UI", 9, "bold"), foreground="#007ACC"
            )
            lbl_code.pack(side="left", anchor="nw")
            
            lbl_name = ttk.Label(
                row_frame, text=h, font=("Segoe UI", 9),
                wraplength=180, justify="left"
            )
            lbl_name.pack(side="left", anchor="nw", fill="x", expand=True)


    @property
    def filtered_indices(self) -> list[int]:
        if hasattr(self.visualization_area, "ranked_indices"):
            return self.visualization_area.ranked_indices
        return []


    def _enable_ctrl(self) -> None:
        self._on_global_change()
