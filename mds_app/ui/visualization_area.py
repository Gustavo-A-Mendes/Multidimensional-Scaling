import tkinter as tk
from tkinter import ttk, messagebox
from tksheet import Sheet
import numpy as np
import numpy.typing as npt
import pandas as pd
from matplotlib.collections import PathCollection, LineCollection
from matplotlib.patches import Ellipse

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from mds_app.custom_widget.scrollable_frame import ScrollableFrame
from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant
from mds_app.utils.validators import *

Matrix = npt.NDArray[np.float64]

class VisualizationArea(ttk.Frame):
    def __init__(self, parent, dataset, mode: str = "group") -> None:
        super().__init__(parent)
        self.parent = parent
        self.dataset: Dataset = dataset
        self.sheet: Sheet | None            = None
        self.notebook: ttk.Notebook | None  = None

        self.id: int | None = None
        self.phase: str = "pre"
        self.selected_group: str = "students"
        self.curr_view = None
        self.ranked_indices: list[int] = []

        # Plot variables
        self.highlight_values = tk.BooleanVar(value=False)
        self.destaque_view_values = tk.BooleanVar(value=True)
        self.mean_view_values = tk.BooleanVar(value=False)
        self.dispersion_view_values = tk.BooleanVar(value=False)
        self.ellipse_view_values = tk.BooleanVar(value=False)
        self.evo_view_values = tk.BooleanVar(value=False)
        self.all_selection_values = tk.BooleanVar(value=False)

        # Variables for ranking filter (in ControlPanel but owned/initialized here)
        self.ranking_mode_var = tk.StringVar(value="Todos os Alunos")
        self.ranking_n_var = tk.IntVar(value=5)

        self.tags: list[tk.BooleanVar] = [
            self.highlight_values,
            self.destaque_view_values,
            self.mean_view_values,
            self.dispersion_view_values,
            self.ellipse_view_values,
            self.evo_view_values
        ]
        self.dataset_mode = mode

        self._create_widgets()

    def _create_widgets(self) -> None:
        if self.notebook:
            return

        self.notebook = ttk.Notebook(self)

        # Aba de início padrão
        initial_tab = ttk.Frame(self.notebook)
        initial_label = ttk.Label(
            initial_tab,
            text="Bem-vindo ao Analisador MDS",
            font=("Segoe UI", 12, "bold")
        )
        self.notebook.add(initial_tab, text="Início")
        initial_label.pack(pady=20)
        
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.get_current_tab())

    def create_dataframe(self) -> None:
        # Limpar abas de dados anteriores
        tabs = self.notebook.tabs()
        for tab in tabs:
            if self.notebook.tab(tab, "text") not in ("Início"):
                self.notebook.forget(tab)

        data_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(data_tab, text="Dados")
        self.notebook.select(data_tab)

        # Planilha ocupa o espaço total
        self.sheet = Sheet(
            data_tab,
            data=[],
            headers=[],
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            show_top_left=True
        )
        self.sheet.enable_bindings(
            "single_select",
            "select_all",
            "row_select",
            "column_select",
            "drag_select",
            "arrowkeys",
            "row_height_resize",
            "column_width_resize",
            "double_click_column_resize",
            "double_click_row_resize",
            "rc_select",
            "copy"
        )
        self.sheet.pack(fill="both", expand=True)

    def create_mds(self) -> None:
        if not self.dataset:
            messagebox.showerror("Erro", "Dados não encontrados.")
            return

        # Limpar aba MDS view anterior
        notebook = self.notebook
        tabs = notebook.tabs()
        for tab in tabs:
            if notebook.tab(tab, "text") in ("MDS view"):
                notebook.forget(tab)

        mds_tab = ttk.Frame(self.notebook, padding=10)
        notebook.add(mds_tab, text="MDS view")
        notebook.select(mds_tab)
        
        # Forçar a renderização imediata da nova aba para que ela ganhe suas dimensões reais
        self.winfo_toplevel().update()

        # Plot e barra de ferramentas
        self.fig, self.ax = plt.subplots(figsize=(5, 5))

        self.toolbar_frame = ttk.Frame(mds_tab)
        self.toolbar_frame.pack(side="bottom", fill="x")

        self.canvas = FigureCanvasTkAgg(self.fig, mds_tab)
        self.canvas.get_tk_widget().configure(width=350, height=350)

        self.nav_toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.nav_toolbar.update()

        s_participants = self.dataset.participants.get("students", []) if self.dataset.participants else []
        self.num_concepts = len(self.dataset.headers) if self.dataset.headers else 0
        self.num_participants = len(s_participants)

        self.p_mean_view = tk.BooleanVar(value=False)
        self.s_mean_view = tk.BooleanVar(value=False)
        self.ellipses_view = tk.BooleanVar(value=False)

        cmap = plt.get_cmap('tab20')

        # Re-inicializar visibilidade dos conceitos
        if not hasattr(self, "concept_visibility") or len(self.concept_visibility) != self.num_concepts:
            self.concept_visibility = [tk.BooleanVar(value=True) for _ in range(self.num_concepts)]

        # Preparar os scatter plots dos conceitos
        self.ax.clear()
        self.scatters = []
        for i in range(self.num_concepts):
            scat = self.ax.scatter(x=[], y=[], color=cmap(i % 20), label=f"C{i + 1}", marker='o')
            self.scatters.append(scat)

        self.p_mean_scatter = []
        for i in range(self.num_concepts):
            scat = self.ax.scatter(x=[], y=[], color=cmap(i % 20), label=f"C{i + 1}", marker='x')
            self.p_mean_scatter.append(scat)

        self.s_mean_scatter = []
        for i in range(self.num_concepts):
            scat = self.ax.scatter(x=[], y=[], color=cmap(i % 20), label=f"C{i + 1}", marker='o')
            self.s_mean_scatter.append(scat)

        self.concept_labels = []
        for i in range(self.num_concepts):
            txt = self.ax.text(
                0, 0, "", fontsize=9, fontweight='bold',
                color=cmap(i % 20), ha='center', va='center', visible=False
            )
            self.concept_labels.append(txt)

        self.ellipses = []
        for i in range(self.num_concepts):
            ellipse = Ellipse(
                xy=(0, 0), width=0, height=0, angle=0,
                edgecolor=cmap(i % 20), facecolor='none', linewidth=1.5,
                alpha=0.60, zorder=2
            )
            self.ax.add_patch(ellipse)
            self.ellipses.append(ellipse)

        self.connection_lines = LineCollection([], colors='gray', linewidths=1, linestyles='--', alpha=0.5, zorder=1)
        self.ax.add_collection(self.connection_lines)
        
        self.evo_lines = LineCollection([], colors='green', linewidths=1.5, linestyles='-', alpha=0.6, zorder=1)
        self.ax.add_collection(self.evo_lines)

        self.reset_view()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

    def refresh(self):
        if not self.notebook:
            return

        headers = self.dataset.headers if self.dataset else None
        has_students = self.dataset.participants and len(self.dataset.participants.get("students", [])) > 0 if self.dataset else False
        has_professors = self.dataset.participants and len(self.dataset.participants.get("professors", [])) > 0 if self.dataset else False

        if headers and (has_students or has_professors):
            self.show_matrix(headers)
            self.show_mds()
        else:
            tabs = self.notebook.tabs()
            for tab in tabs:
                if self.notebook.tab(tab, "text") not in ("Início"):
                    self.notebook.forget(tab)
            self.notebook.select(0)

    def show_matrix(self, headers: list[str]) -> None:
        highlight = self.highlight_values.get()

        if not self.dataset or not self.dataset.participants:
            self._clear_sheet()
            return

        s_participants = self.dataset.participants.get("students", [])
        p_participants = self.dataset.participants.get("professors", [])

        # Verificar se ID é válido
        if self.selected_group == "students":
            if self.id is None or self.id < 0 or self.id >= len(s_participants):
                self._clear_sheet()
                return
        else:
            if self.id is None or self.id < 0 or self.id >= len(p_participants):
                self._clear_sheet()
                return

        self.sheet.set_sheet_data([])
        self.sheet.headers([])
        self.sheet.row_index([])

        # Carregar matriz com base na seleção
        if self.s_mean_view.get():
            actual_phase = "pos" if self.phase == "pos" else "pre"
            mean_key = f"students_{actual_phase}"
            np2df = pd.DataFrame(data=self.dataset.mean[mean_key], index=headers, columns=headers)
            df = np2df.loc[headers, headers]
        else:
            actual_phase = "pos" if self.phase == "pos" else "pre"
            if self.selected_group == "professors":
                p = p_participants[self.id]
                participant_df = p.dataframe_pos if p.dataframe_pos is not None else p.dataframe_pre
            else:
                p = s_participants[self.id]
                participant_df = getattr(p, f"dataframe_{actual_phase}")
                if participant_df is None:
                    participant_df = p.dataframe_pre
            
            if participant_df is not None:
                df = participant_df.loc[headers, headers]
            else:
                df = pd.DataFrame(np.nan, index=headers, columns=headers)

        generic_headers = [self.dataset.concept_mapping.get(h, h) for h in headers]
        self.sheet.headers(generic_headers)
        self.sheet.row_index(generic_headers)

        dados = df.values.tolist()
        self.sheet.set_sheet_data(dados)
        self.sheet.dehighlight_all()

        # Destaque de cores na tabela
        num = len(headers)
        if highlight:
            valid_values = []
            for r in range(num):
                for c in range(num):
                    if r > c:
                        v = df.iloc[r, c]
                        if pd.notna(v) and isinstance(v, (int, float)):
                            valid_values.append(v)
            min_val = 0.0
            max_val = max(valid_values) if valid_values else 9.0
            if max_val <= 0.0:
                max_val = 1.0

        readonly_list = []
        diagonal_cells = []
        upper_triangle_cells = []
        lower_triangle_groups = {}

        for r in range(num):
            for c in range(num):
                if r <= c:
                    readonly_list.append((r, c))
                    if r == c:
                        diagonal_cells.append((r, c))
                    else:
                        upper_triangle_cells.append((r, c))
                else:
                    if not highlight:
                        cor = "#f0f0f0" if r % 2 == 0 else "#ffffff"
                    else:
                        v = df.iloc[r, c]
                        cor = self.value_to_color(v, min_val, max_val)
                    
                    key = (cor, "black")
                    if key not in lower_triangle_groups:
                        lower_triangle_groups[key] = []
                    lower_triangle_groups[key].append((r, c))

        if diagonal_cells:
            self.sheet.highlight_cells(cells=diagonal_cells, bg="#e0e0e0", fg="#808080", redraw=False)
        if upper_triangle_cells:
            self.sheet.highlight_cells(cells=upper_triangle_cells, bg="#f2f2f2", fg="#808080", redraw=False)
        for (bg, fg), cells in lower_triangle_groups.items():
            if cells:
                self.sheet.highlight_cells(cells=cells, bg=bg, fg=fg, redraw=False)

        try:
            self.sheet.readonly_cells(cells=readonly_list)
        except Exception as e:
            print(f"tksheet readonly_cells fallback: {e}")

        size = 40
        self.sheet.set_options(
            header_bg="#d9d9d9", header_fg="black",
            index_bg="#d9d9d9", index_fg="black",
            show_empty_rows=False,
        )
        self.sheet.set_all_column_widths(size)
        self.sheet.set_all_row_heights(size)
        self.sheet.refresh()

    def _clear_sheet(self) -> None:
        if self.sheet:
            self.sheet.set_sheet_data([])
            self.sheet.headers([])
            self.sheet.row_index([])
            self.sheet.refresh()

    def reset_view(self):
        self.ax.autoscale()
        self.canvas.draw()

    def show_mds(self) -> None:
        p_participants = self.dataset.participants.get("professors") if self.dataset.participants else None
        s_participants = self.dataset.participants.get("students") if self.dataset.participants else None
        
        if not p_participants and not s_participants:
            return
            
        has_students = s_participants and len(s_participants) > 0
        has_professors = p_participants and len(p_participants) > 0

        # Garantir ID válido do estudante para plot
        student_id = self.id if (self.selected_group == "students" and self.id is not None) else 0
        if has_students and (student_id < 0 or student_id >= len(s_participants)):
            student_id = 0

        if has_students:
            def get_valid_mds(p_list, ph):
                res = []
                for p in p_list:
                    mds = getattr(p, f"mds_result_{ph}")
                    if mds and mds.X_aligned is not None:
                        res.append(mds.X_aligned)
                    else:
                        if p.mds_result_pre and p.mds_result_pre.X_aligned is not None:
                            res.append(p.mds_result_pre.X_aligned)
                        else:
                            num_concepts = len(self.dataset.headers)
                            res.append(np.full((num_concepts, 2), np.nan))
                return np.array(res)

            self.mds_results_pre = get_valid_mds(s_participants, "pre")
            self.mds_results_pos = get_valid_mds(s_participants, "pos")
            
            actual_phase = "pos" if self.phase == "pos" else "pre"
            self.mds_results = self.mds_results_pos if self.phase == "pos" else self.mds_results_pre
        else:
            self.mds_results_pre = None
            self.mds_results_pos = None
            self.mds_results = None

        p_centr_ref = self.dataset.centroids.get("professors") if self.dataset.centroids else None
        p_centroids = p_centr_ref.copy() if p_centr_ref is not None else None
        
        if has_students:
            ranked_indices = self.get_ranked_indices(p_centroids)
            
            if self.ranked_indices != ranked_indices:
                self.ranked_indices = ranked_indices
                self.event_generate("<<RankingUpdated>>")
            else:
                self.ranked_indices = ranked_indices

            if self.ranking_mode_var.get() != "Todos os Alunos" and len(ranked_indices) > 0:
                filtered_mds = self.mds_results[ranked_indices]
                s_centroids = np.nanmean(filtered_mds, axis=0)
                s_stds = np.nanstd(filtered_mds, axis=0)
            else:
                if len(self.mds_results) > 0:
                    s_centroids = np.nanmean(self.mds_results, axis=0)
                    s_stds = np.nanstd(self.mds_results, axis=0)
                else:
                    s_centroids = None
                    s_stds = None
        else:
            ranked_indices = []
            s_centroids = None
            s_stds = None

        highlight   = self.tags[0].get()
        destaque    = self.tags[1].get()
        mean        = self.tags[2].get()
        dispersion  = self.tags[3].get()
        ellipsis    = self.tags[4].get()

        # Selecionar Tudo / Caixas
        if hasattr(self, "concept_visibility"):
            count_visible = np.array([v.get() for v in self.concept_visibility])
            if np.all(count_visible):
                self.all_selection_values.set(True)
            else:
                self.all_selection_values.set(False)

        self.p_mean_view.set(mean and has_professors)
        self.ellipses_view.set(ellipsis and has_students)

        if dispersion and has_students:
            curr_mds = self.mds_results[ranked_indices]
        elif has_students:
            curr_mds = np.array([self.mds_results[student_id]])
        else:
            curr_mds = None

        # 1. Plot dos pontos dos alunos
        for i, scat in enumerate(self.scatters):
            visibility = has_students and self.concept_visibility[i].get() and (not self.s_mean_view.get() or dispersion)
            scat.set_visible(visibility)

            if visibility and curr_mds is not None:
                xs = curr_mds[:, i, 0]
                ys = curr_mds[:, i, 1]
                scat.set_offsets(np.column_stack((xs, ys)))

        # 2. Plot da média dos professores (gabarito)
        for i, scat in enumerate(self.p_mean_scatter):
            visibility = self.concept_visibility[i].get() and self.p_mean_view.get() and p_centroids is not None
            scat.set_visible(visibility)

            if visibility and p_centroids is not None:
                p_ys = p_centroids[i, 1]
                p_xs = p_centroids[i, 0]
                scat.set_offsets(np.column_stack((p_xs, p_ys)))

        # 3. Plot da média da sala
        for i, scat in enumerate(self.s_mean_scatter):
            visibility = has_students and self.concept_visibility[i].get() and self.s_mean_view.get() and s_centroids is not None
            scat.set_visible(visibility)

            if visibility and s_centroids is not None:
                s_ys = s_centroids[i, 1]
                s_xs = s_centroids[i, 0]
                scat.set_offsets(np.column_stack((s_xs, s_ys)))

        # 4. Rótulos dos conceitos
        limite = self.dataset.get_global_limits()
        plot_range = limite[1] - limite[0]
        proximity_threshold = 0.06 * plot_range
        placed_positions = []
        
        offsets = [
            (0.0, 0.12), (0.0, -0.22), (0.18, -0.05), (-0.18, -0.05),
            (0.13, 0.13), (-0.13, -0.18), (0.13, -0.18), (-0.13, 0.13)
        ]

        for i, txt in enumerate(self.concept_labels):
            visibility = self.concept_visibility[i].get() and (
                (destaque and has_students) or 
                (self.s_mean_view.get() and s_centroids is not None) or 
                (self.p_mean_view.get() and not has_students and p_centroids is not None)
            )
            txt.set_visible(visibility)

            if visibility:
                generic_name = self.dataset.concept_mapping.get(self.dataset.headers[i], f"C{i+1}")
                txt.set_text(generic_name)

                if self.s_mean_view.get() and s_centroids is not None:
                    x, y = s_centroids[i, 0], s_centroids[i, 1]
                elif not has_students and p_centroids is not None:
                    x, y = p_centroids[i, 0], p_centroids[i, 1]
                else:
                    x, y = curr_mds[0, i, 0], curr_mds[0, i, 1]

                collision_count = 0
                for px, py in placed_positions:
                    if np.sqrt((x - px)**2 + (y - py)**2) < proximity_threshold:
                        collision_count += 1
                
                offset_idx = collision_count % len(offsets)
                dx, dy = offsets[offset_idx]
                
                scaled_dx = dx * (plot_range / 10.0)
                scaled_dy = dy * (plot_range / 10.0)

                txt.set_position((x + scaled_dx, y + scaled_dy))
                placed_positions.append((x, y))

        # 5. Elipses de dispersão
        for i, ellipse in enumerate(self.ellipses):
            visibility = has_students and self.concept_visibility[i].get() and self.ellipses_view.get() and s_centroids is not None and s_stds is not None
            ellipse.set_visible(visibility)

            if visibility and s_centroids is not None and s_stds is not None:
                center = (s_centroids[i, 0], s_centroids[i, 1])
                ellipse.set_center(center)
                ellipse.set_width(s_stds[i, 0] * 4)
                ellipse.set_height(s_stds[i, 1] * 4)

        # 6. Linhas de conexão ao Gabarito
        segmentos = []
        for i in range(self.num_concepts):
            if self.concept_visibility[i].get():
                if mean and p_centroids is not None:
                    pos_prof = p_centroids[i]
                    if not self.s_mean_view.get() and has_students and curr_mds is not None:
                        pos_dest = curr_mds[0, i] if not dispersion else self.mds_results[student_id, i]
                        segmentos.append([pos_prof, pos_dest])

                    if self.s_mean_view.get() and s_centroids is not None:
                        pos_stud = s_centroids[i]
                        segmentos.append([pos_prof, pos_stud])

        self.connection_lines.set_segments(segmentos)
        self.connection_lines.set_visible(len(segmentos) > 0)
        
        # Linhas de evolução (Pré -> Pós)
        show_evo = self.evo_view_values.get()
        if show_evo and self.phase == "pos" and has_students:
            evo_segs = []
            
            if self.s_mean_view.get():
                if self.ranking_mode_var.get() != "Todos os Alunos" and len(ranked_indices) > 0:
                    s_centr_pre = np.mean(self.mds_results_pre[ranked_indices], axis=0)
                    s_centr_pos = s_centroids
                else:
                    s_centr_pre = self.dataset.centroids.get("students_pre")
                    s_centr_pos = self.dataset.centroids.get("students_pos")
                    
                if s_centr_pre is not None and s_centr_pos is not None:
                    for i in range(self.num_concepts):
                        if self.concept_visibility[i].get():
                            evo_segs.append([s_centr_pre[i], s_centr_pos[i]])
            else:
                if dispersion:
                    for i in range(self.num_concepts):
                        if self.concept_visibility[i].get():
                            for j in ranked_indices:
                                evo_segs.append([self.mds_results_pre[j, i], self.mds_results_pos[j, i]])
                else:
                    for i in range(self.num_concepts):
                        if self.concept_visibility[i].get():
                            evo_segs.append([self.mds_results_pre[student_id, i], self.mds_results_pos[student_id, i]])
            
            self.evo_lines.set_segments(evo_segs)
            self.evo_lines.set_visible(len(evo_segs) > 0)
        else:
            self.evo_lines.set_segments([])
            self.evo_lines.set_visible(False)

        # Atualizar opacidade dos pontos (Destaque do indivíduo na dispersão)
        if has_students and curr_mds is not None:
            for i, scat in enumerate(self.scatters):
                face_color = scat.get_facecolor()[0]
                new_colors = np.tile(face_color, (len(curr_mds), 1))
                new_colors[:, 3] = 0.1

                if destaque:
                    if dispersion:
                        try:
                            highlight_idx = ranked_indices.index(student_id)
                            new_colors[highlight_idx, 3] = 1.0
                        except ValueError:
                            pass
                    else:
                        new_colors[0, 3] = 1.0

                scat.set_facecolor(new_colors)
                scat.set_edgecolor(new_colors)

        self.ax.set_xlabel("Dimensão 1")
        self.ax.set_ylabel("Dimensão 2")
        self.ax.grid(True, linestyle='--', alpha=0.5)

        self.ax.set_xlim(limite)
        self.ax.set_ylim(limite)
        self.ax.set_aspect('equal')
        self.fig.tight_layout()
        
        # Forçar a atualização de layouts do Tkinter
        self.winfo_toplevel().update()
        
        # Obter as dimensões reais e forçar o disparo do evento de redimensionamento no Canvas
        canvas_widget = self.canvas.get_tk_widget()
        w = canvas_widget.winfo_width()
        h = canvas_widget.winfo_height()
        canvas_widget.event_generate("<Configure>", width=w, height=h)
        
        # Processar o evento de redimensionamento e realizar o desenho
        self.winfo_toplevel().update()
        self.canvas.draw()

    def get_ranked_indices(self, p_centroids):
        mode = self.ranking_mode_var.get()
        try:
            n = self.ranking_n_var.get()
        except tk.TclError:
            n = 5
            
        num_students = len(self.mds_results)
        all_indices = list(range(num_students))
        
        if mode == "Todos os Alunos" or p_centroids is None:
            return all_indices
            
        distances = []
        if mode in ["Top Alinhados", "Top Divergentes"]:
            for j in range(num_students):
                student_coords = self.mds_results[j]
                if student_coords.shape == p_centroids.shape:
                    dist = np.sum(np.linalg.norm(student_coords - p_centroids, axis=1))
                    distances.append(dist)
                else:
                    distances.append(np.inf if mode == "Top Alinhados" else -np.inf)
                
            sorted_indices = np.argsort(distances)
            if mode == "Top Divergentes":
                sorted_indices = sorted_indices[::-1]
            return sorted_indices[:n].tolist()
            
        elif mode == "Top Evolução":
            if self.mds_results_pre is None or self.mds_results_pos is None:
                return all_indices
                
            for j in range(num_students):
                student_coords_pre = self.mds_results_pre[j]
                student_coords_pos = self.mds_results_pos[j]
                if student_coords_pre.shape == p_centroids.shape and student_coords_pos.shape == p_centroids.shape:
                    dist_pre = np.sum(np.linalg.norm(student_coords_pre - p_centroids, axis=1))
                    dist_pos = np.sum(np.linalg.norm(student_coords_pos - p_centroids, axis=1))
                    distances.append(dist_pre - dist_pos)
                else:
                    distances.append(-np.inf)
                
            sorted_indices = np.argsort(distances)[::-1]
            return sorted_indices[:n].tolist()

    def set_index(self, idx: int, phase: str = "pre", status: str = "default", group: str = "students") -> None:
        self.id = idx
        self.phase = phase
        self.selected_group = group

        if status == "default":
            self.s_mean_view.set(False)
        elif status == "mean":
            self.s_mean_view.set(True)

        self.refresh()

    @staticmethod
    def value_to_color(v: float, min_val: float, max_val: float) -> str:
        if pd.isna(v) or not isinstance(v, (int, float)):
            return "#FFFFFF"

        if max_val > min_val:
            normalized = (v - min_val) / (max_val - min_val)
        else:
            normalized = 0.0

        normalized = max(0.0, min(1.0, normalized))

        colors = ["#96C8FF", "#96FFE1", "#64FF96", "#C8FF7D", "#FFFF64", "#FFC832", "#FF9632", "#FF7D64", "#FF644B", "#FF3232"]
        custom_cmap = mcolors.LinearSegmentedColormap.from_list("custom_spectral", colors)
        rgb = custom_cmap(normalized)[:3]

        return mcolors.to_hex(rgb)

    def get_current_tab(self) -> None:
        notebook = self.notebook
        tab = notebook.tab(notebook.select(), "text")
        unicoded_name = unicode_text(tab)
        treated_name = unicoded_name.lower().replace(" ", "_")
        self.curr_view = treated_name

    def set_mode(self, mode: str) -> None:
        self.dataset_mode = mode
        self.id = 0
        self.refresh()