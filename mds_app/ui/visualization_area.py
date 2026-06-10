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
import matplotlib.pyplot as plt

from mds_app.custom_widget.scrollable_frame import ScrollableFrame
from mds_app.data import participant
from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant
from mds_app.utils.validators import *

Matrix = npt.NDArray[np.float64]

class VisualizationArea(ttk.Frame):
    def __init__(self, parent, dataset, mode: str = "group") -> None:
        super().__init__(parent)

        self.dataset: Dataset = dataset
        self.sheet: Sheet | None            = None
        self.notebook: ttk.Notebook | None  = None
        # self.mds_session = None

        self.id: int | None = None
        self.phase: str = "pre"
        self.curr_view = None
        self.ranked_indices: list[int] = []

        # plot attributes:
        self.highlight_checkbox: ttk.Checkbutton | None = None
        self.highlight_values = tk.BooleanVar(value=False)

        self.destaque_view_checkbox: ttk.Checkbutton | None = None
        self.destaque_view_values = tk.BooleanVar(value=True)

        self.mean_view_checkbox: ttk.Checkbutton | None = None
        self.mean_view_values = tk.BooleanVar(value=False)

        self.dispersion_view_checkbox: ttk.Checkbutton | None = None
        self.dispersion_view_values = tk.BooleanVar(value=False)

        self.ellipse_view_checkbox: ttk.Checkbutton | None = None
        self.ellipse_view_values = tk.BooleanVar(value=False)

        self.evo_view_checkbox: ttk.Checkbutton | None = None
        self.evo_view_values = tk.BooleanVar(value=False)

        self.all_selection_checkbox: ttk.Checkbutton | None = None
        self.all_selection_values = tk.BooleanVar(value=False)

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

    # create the visualization area (notebook):
    def _create_widgets(self) -> None:
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # notebook:
        if self.notebook:
            return

        self.notebook = ttk.Notebook(self)

        # ----------------------------------------------------------------------
        # initial tab:
        # ----------------------------------------------------------------------

        # frame:
        initial_tab = ttk.Frame(self.notebook)

        # label:
        initial_label = ttk.Label(
            initial_tab,
            text="Bem-vindo ao Analisador MDS",
            font=("Segoe UI", 12, "bold")
        )

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------

        # adding tab:
        self.notebook.add(initial_tab, text="Início")

        initial_label.pack(pady=20)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", lambda e: self.get_current_tab)

    # plot dataframe in visualization area:
    def create_dataframe(self) -> None:
        # ----------------------------------------------------------------------
        # clear layout:
        # ----------------------------------------------------------------------

        # clear data tabs:
        tabs = self.notebook.tabs()
        for tab in tabs:
            if self.notebook.tab(tab, "text") not in ("Início"):
                self.notebook.forget(tab)

        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # notebook tab:
        data_tab = ttk.Frame(self.notebook)
        self.notebook.add(data_tab, text=f"Dados")
        self.notebook.select(data_tab)
        # self.notebook.add(tab, text=f"{participant["name"]}{len(self.notebook.tabs())}")

        # panedwindow:
        self.data_view = tk.PanedWindow(data_tab, orient="horizontal")
        self.data_view.pack(pady=10, fill="both", expand=True)

        self.data_content = ttk.Frame(self.data_view)
        self.data_ctrl = ScrollableFrame(self.data_view)

        self.data_view.add(self.data_content, minsize=100, stretch="always")
        self.data_view.add(self.data_ctrl, minsize=100, stretch="never")
        self.update()  # Força atualização completa do layout geométrico para obter a largura real
        self.data_view.sash_place(0, self.data_view.winfo_width() - 250, 0)

        # sheet
        self.sheet = Sheet(
            self.data_content,
            data=[],
            headers=[],
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            show_top_left = True
        )
        self.sheet.enable_bindings(
            "single_select",
            "row_select",
            "column_select",
            "drag_select",
            "arrowkeys",
            "row_height_resize",
            "column_width_resize",
            "double_click_column_resize",
            "double_click_row_resize",
            "rc_select",
            "edit_cell"
        )
        self.sheet.extra_bindings([("end_edit_cell", self.on_cell_edited), ("select_cell", self.on_select_cell)])

        # -----
        ctrl_frame = self.data_ctrl.content
        ttk.Label(ctrl_frame, text="Controles da Matriz").pack(pady=5)

        # highlight:
        self.highlight_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Destacar dados",
            command=self._hightlight_values,
            variable=self.highlight_values,
            onvalue=True,
            offvalue=False
        )
        self.highlight_checkbox.pack(fill="x", padx=10)


        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------

        self.sheet.pack(fill="both", expand=True)

    # configure and stilyze data placement:
    def create_mds(self) -> None:
        # the dataset must not be empty:
        if not self.dataset:
            messagebox.showerror(
                "Erro", "Dados não encontrados."
            )
            return

        # it will create two tabs: MDS_config and MDS_result:

        # clear MDS tabs:
        notebook = self.notebook
        tabs = notebook.tabs()
        for tab in tabs:
            if notebook.tab(tab, "text") in ("MDS view"):
                notebook.forget(tab)

        mds_tab = ttk.Frame(self.notebook)
        notebook.add(mds_tab, text="MDS view")
        notebook.select(mds_tab)

        # panedwindow:
        self.mds_view = tk.PanedWindow(mds_tab, orient="horizontal")
        self.mds_view.pack(pady=10, fill="both", expand=True)

        self.mds_content = ttk.Frame(self.mds_view)
        self.mds_ctrl = ScrollableFrame(self.mds_view)

        self.mds_view.add(self.mds_content, minsize=100, stretch="always")
        self.mds_view.add(self.mds_ctrl, minsize=100, stretch="never")
        self.update()  # Força atualização completa do layout geométrico para obter a largura real
        self.mds_view.sash_place(0, self.mds_view.winfo_width() - 250, 0)

        ttk.Label(self.mds_content, text="Configuração da Análise",
                  font=("Arial", 12, "bold")).pack(pady=10)

        # Área de visualização

        # Criando Figure do plot com constrained_layout e base (6, 6) compacta para evitar transbordamento inicial
        self.fig, self.ax = plt.subplots(figsize=(6, 6), constrained_layout=True)

        # Contêiner dedicado para a barra de ferramentas na parte inferior
        self.toolbar_frame = ttk.Frame(self.mds_content)
        self.toolbar_frame.pack(side="bottom", fill="x")

        self.canvas = FigureCanvasTkAgg(self.fig, self.mds_content)

        # Associamos a barra de ferramentas ao contêiner dedicado inferior
        self.nav_toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.nav_toolbar.update()

        # ==================================================
        s_participants = self.dataset.participants["students"]

        self.num_concepts = len(self.dataset.headers)
        self.num_participants = len(s_participants)
        self.p_mean_view = tk.BooleanVar(value=False)
        self.s_mean_view = tk.BooleanVar(value=False)
        self.ellipses_view = tk.BooleanVar(value=False)

        #
        cmap = plt.get_cmap('tab20')

        self.concept_visibility = [tk.BooleanVar(value=True) for _ in range(self.num_concepts)]

        ctrl_frame = self.mds_ctrl.content
        ttk.Label(ctrl_frame, text="Controles do Plot").pack(pady=5)

        # destaque view:
        self.destaque_view_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Visualizar em destaque",
            command=self._destaque_view_values,
            variable=self.destaque_view_values,
            onvalue=True,
            offvalue=False,
        )
        self.destaque_view_checkbox.pack(fill="x", padx=10)

        # mean view:
        self.mean_view_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Visualizar gabarito",
            command=self._mean_view_values,
            variable=self.mean_view_values,
            onvalue=True,
            offvalue=False
        )
        self.mean_view_checkbox.pack(fill="x", padx=10)

        # dispersion view:
        self.dispersion_view_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Visualizar dispersão",
            command=self._dispersion_view_values,
            variable=self.dispersion_view_values,
            onvalue=True,
            offvalue=False
        )
        self.dispersion_view_checkbox.pack(fill="x", padx=10)

        # elipse view:
        self.ellipse_view_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Visualizar zona de dispersão",
            command=self._ellipse_view_values,
            variable=self.ellipse_view_values,
            onvalue=True,
            offvalue=False,
        )
        self.ellipse_view_checkbox.pack(fill="x", padx=10)

        # evolution view:
        self.evo_view_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Visualizar evolução",
            command=self._evo_view_values,
            variable=self.evo_view_values,
            onvalue=True,
            offvalue=False,
            state="disabled"
        )
        self.evo_view_checkbox.pack(fill="x", padx=10)

        ttk.Separator(ctrl_frame).pack(fill="x", padx=10, pady=10)

        # --- Ranking ---
        self.ranking_frame = ttk.LabelFrame(ctrl_frame, text="Filtro de Ranking", padding=5)
        self.ranking_frame.pack(fill="x", padx=10, pady=5)
        
        self.ranking_mode_var = tk.StringVar(value="Todos os Alunos")
        self.ranking_combo = ttk.Combobox(
            self.ranking_frame, 
            textvariable=self.ranking_mode_var,
            values=["Todos os Alunos", "Top Alinhados", "Top Divergentes", "Top Evolução"],
            state="readonly"
        )
        self.ranking_combo.pack(fill="x", pady=2)
        self.ranking_combo.bind("<<ComboboxSelected>>", lambda e: self.atualizar_estado_ranking())
        
        spin_frame = ttk.Frame(self.ranking_frame)
        spin_frame.pack(fill="x", pady=2)
        self.quantidade_label = ttk.Label(spin_frame, text="Quantidade (N):")
        self.quantidade_label.pack(side="left")

        self.ranking_n_var = tk.IntVar(value=5)
        self.ranking_spin = ttk.Spinbox(
            spin_frame, from_=1, to=self.num_participants, width=5, textvariable=self.ranking_n_var
        )
        self.ranking_spin.pack(side="right")
        self.ranking_combo.bind("<<ComboboxSelected>>", lambda e: self.atualizar_estado_ranking())
        self.ranking_combo.bind("<Return>", lambda e: self.atualizar_estado_ranking())
        self.ranking_spin.bind("<Return>", lambda e: self.show_mds())
        
        def _on_spin_change(*args):
            try:
                # Se for número válido e maior que 0, atualiza
                val = self.ranking_n_var.get()
                if val > 0:
                    self.show_mds()
            except Exception as e:
                # Impede que o Tkinter quebre silenciosamente o trace
                print(f"Silenced error in spin change: {e}")
                
        self.ranking_n_var.trace_add("write", _on_spin_change)

        ttk.Separator(ctrl_frame).pack(fill="x", padx=10, pady=10)

        self.all_selection_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Selecionar Tudo",
            variable=self.all_selection_values,
            command=self.select_all
        )
        self.all_selection_checkbox.pack(side="top", padx=5, anchor='w')

        for i in range(self.num_concepts):
            header = self.dataset.headers[i]
            generic_name = self.dataset.concept_mapping.get(header, f"C{i+1}")
            btn = ttk.Checkbutton(
                ctrl_frame,
                text=generic_name,
                variable=self.concept_visibility[i],
                command=self.show_mds
            )
            btn.pack(side="top", padx=5, anchor='w')

        # chk_labels = ttk.Checkbutton(ctrl_frame, text="Mostrar nomes")
        # chk_labels.pack(side="top", padx=5, anchor='w')
        #
        # chk_grid = ttk.Checkbutton(ctrl_frame, text="Mostrar grid")
        # chk_grid.pack(side="top", padx=5, anchor='w')

        self.reset_view()

        # O canvas é empacotado no topo e expande para preencher o espaço restante,
        # enquanto a toolbar_frame já está garantida e empacotada na base (bottom)
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Desabilita a propagação de empacotamento no contêiner para travar seu tamanho
        # ao espaço estritamente definido pelo PanedWindow, impedindo que chamadas de draw()
        # forcem o crescimento do frame e cortem o gráfico
        self.mds_content.pack_propagate(False)

        # set list of scatter to plot data:
        self.scatters = []
        for i in range(self.num_concepts):
            scat = self.ax.scatter(x=[], y=[], color=cmap(i % 20), label=f"C{i + 1}", marker='o')
            self.scatters.append(scat)

        # create mean scatters:
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
            # Criamos o texto na origem (0,0) e invisível
            txt = self.ax.text(
                0, 0,
                "",  # String vazia por enquanto
                fontsize=9,
                fontweight='bold',
                color=cmap(i % 20),  # Mesma cor do conceito
                ha='center',  # Alinhamento horizontal: centro
                va='center',  # Alinhamento vertical centralizado para melhor encaixe das direções de offsets
                visible=False
            )
            self.concept_labels.append(txt)

        # Criando a elipse de dispersão
        self.ellipses = []
        for i in range(self.num_concepts):
            ellipse = Ellipse(
                xy=(0, 0),
                width=0,
                height=0,
                angle=0,  # MDS clássico não gera correlação rotacional intrínseca aqui
                edgecolor=cmap(i % 20),
                facecolor='none',
                linewidth=1.5,
                alpha=0.60,  # Transparência para não poluir o gráfico
                # label='Dispersão' if i == 0 else ""
                zorder=2
            )
            self.ax.add_patch(ellipse)
            self.ellipses.append(ellipse)

        self.connection_lines = LineCollection([], colors='gray', linewidths=1, linestyles='--', alpha=0.5,
                                               zorder=1)
        self.ax.add_collection(self.connection_lines)
        
        self.evo_lines = LineCollection([], colors='green', linewidths=1.5, linestyles='-', alpha=0.6,
                                               zorder=1)
        self.ax.add_collection(self.evo_lines)
        self.set_mode(self.dataset_mode)

    #
    def refresh(self):
        if not self.notebook:
            return

        header = self.dataset.headers if self.dataset else None
        has_students = self.dataset.participants and len(self.dataset.participants.get("students", [])) > 0 if self.dataset else False
        
        if header and has_students:
            self.show_matrix(header)
            if hasattr(self, "ranking_combo") and self.ranking_combo:
                self.atualizar_estado_ranking()
                self.show_mds()
        else:
            # Limpar e esquecer abas que não sejam "Início"
            tabs = self.notebook.tabs()
            for tab in tabs:
                if self.notebook.tab(tab, "text") not in ("Início"):
                    self.notebook.forget(tab)
            # Selecionar aba Início
            self.notebook.select(0)

    #
    def show_matrix(self, headers: list[str]) -> None:
        highlight = self.highlight_values.get()

        if not self.dataset or not self.dataset.participants:
            if self.sheet:
                self.sheet.set_sheet_data([])
                self.sheet.headers([])
                self.sheet.row_index([])
                self.sheet.refresh()
            return

        p_participants = self.dataset.participants.get("professors", [])
        s_participants = self.dataset.participants.get("students", [])
        participants = p_participants + s_participants
        
        if self.id is None or self.id < 0 or not s_participants or self.id >= len(s_participants):
            self.sheet.set_sheet_data([])
            self.sheet.headers([])
            self.sheet.row_index([])
            self.sheet.refresh()
            return
        # -----------------------------
        # clear sheet:
        # -----------------------------
        self.sheet.set_sheet_data([])       # clear data
        self.sheet.headers([])              # clear header
        self.sheet.row_index([])            # clear index

        # -----------------------------
        # define sheet header and index:
        # -----------------------------

        if self.s_mean_view.get():
            actual_phase = "pos" if self.phase == "pos" else "pre"
            mean_key = f"students_{actual_phase}"
            np2df = pd.DataFrame(data=self.dataset.mean[mean_key], index=headers, columns=headers)
            df = np2df.loc[headers, headers]
        else:
            actual_phase = "pos" if self.phase == "pos" else "pre"
            participant_df = getattr(s_participants[self.id], f"dataframe_{actual_phase}")
            if participant_df is None:
                participant_df = s_participants[self.id].dataframe_pre
            
            if participant_df is not None:
                df = participant_df.loc[headers, headers]
            else:
                df = pd.DataFrame(np.nan, index=headers, columns=headers)

        generic_headers = [self.dataset.concept_mapping.get(h, h) for h in headers]
        self.sheet.headers(generic_headers)
        self.sheet.row_index(generic_headers)

        # -----------------------------
        # insert (and style) data:
        # -----------------------------
        dados = df.values.tolist()
        self.sheet.set_sheet_data(dados)

        # clear style:
        self.sheet.dehighlight_all()

        readonly_list = []
        num = len(dados)
        for r in range(num):
            for c in range(num):
                if r <= c:
                    readonly_list.append((r, c))
                    bg_color = "#e0e0e0" if r == c else "#f2f2f2"
                    fg_color = "#808080"
                    self.sheet.highlight_cells(row=r, column=c, bg=bg_color, fg=fg_color)
                else:
                    if not highlight:   # default style
                        cor = "#f0f0f0" if r % 2 == 0 else "#ffffff"
                    else:               # highlight style
                        cor = self.value_to_color(df, r, c)
                    self.sheet.highlight_cells(row=r, column=c, bg=cor, fg="black")

        try:
            # Tentar limpar qualquer marcação de readonly anterior e definir as novas
            self.sheet.readonly_cells(cells=readonly_list)
        except Exception as e:
            print(f"tksheet readonly_cells fallback: {e}")

        # -----------------------------
        # adjusting appearance:
        # -----------------------------
        size = 40
        self.sheet.set_options(
            header_bg="#d9d9d9",
            header_fg="black",
            index_bg="#d9d9d9",
            index_fg="black",
            show_empty_rows=False,
        )

        self.sheet.set_all_column_widths(size)
        self.sheet.set_all_row_heights(size)

        # redraw the sheet:
        self.sheet.refresh()

    #
    def reset_view(self):
        self.ax.autoscale()
        self.canvas.draw()

    #
    def show_mds(self) -> None:
        p_participants = self.dataset.participants.get("professors") if self.dataset.participants else None
        s_participants = self.dataset.participants.get("students") if self.dataset.participants else None
        
        if not p_participants and not s_participants:
            return
            
        participants = (p_participants or []) + (s_participants or [])
        
        if self.id is None or self.id < 0 or not s_participants or self.id >= len(s_participants):
            self.ax.clear()
            self.ax.set_xlabel("Dimensão 1")
            self.ax.set_ylabel("Dimensão 2")
            self.ax.grid(True, linestyle='--', alpha=0.5)
            self.canvas.draw_idle()
            return

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

        p_centr_ref = self.dataset.centroids.get("professors")
        s_centr_ref = self.dataset.centroids.get(f"students_{actual_phase}")
        p_stds_ref = self.dataset.stds.get("professors")
        s_stds_ref = self.dataset.stds.get(f"students_{actual_phase}")

        p_centroids = p_centr_ref.copy() if p_centr_ref is not None else None
        
        ranked_indices = self.get_ranked_indices(p_centroids)
        
        # Guardar e notificar o painel via evento (evita dependência cíclica)
        if hasattr(self, "ranked_indices") and self.ranked_indices != ranked_indices:
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
            
        p_stds = p_stds_ref.copy() if p_stds_ref is not None else None

        highlight   = self.tags[0].get()
        destaque    = self.tags[1].get()
        mean        = self.tags[2].get()
        dispersion  = self.tags[3].get()
        ellipsis    = self.tags[4].get()

        count_visible = np.array([v.get() for v in self.concept_visibility])
        if np.all(count_visible):
            self.all_selection_values.set(True)
        elif np.all(count_visible == False):
            self.all_selection_values.set(False)
        else:
            self.all_selection_values.set(False)
            self.all_selection_checkbox.state(['alternate'])

        if mean:
            self.p_mean_view.set(True)
        else:
            self.p_mean_view.set(False)

        if ellipsis:
            self.ellipses_view.set(True)
        else:
            self.ellipses_view.set(False)

        if dispersion:
            curr_mds = self.mds_results[ranked_indices]
        else:
            curr_mds = np.array([self.mds_results[self.id]])

        # students plot:
        for i, scat in enumerate(self.scatters):
            visibility = self.concept_visibility[i].get() and (not self.s_mean_view.get() or dispersion)
            scat.set_visible(visibility)

            if visibility:
                xs = curr_mds[:, i, 0]
                ys = curr_mds[:, i, 1]
                scat.set_offsets(np.column_stack((xs, ys)))

        # professors mean:
        for i, scat in enumerate(self.p_mean_scatter):
            visibility = self.concept_visibility[i].get() and self.p_mean_view.get() and p_centroids is not None
            scat.set_visible(visibility)

            if visibility and p_centroids is not None:
                p_ys = p_centroids[i, 1]
                p_xs = p_centroids[i, 0]
                scat.set_offsets(np.column_stack((p_xs, p_ys)))

        # class mean:
        for i, scat in enumerate(self.s_mean_scatter):
            visibility = self.concept_visibility[i].get() and self.s_mean_view.get() and s_centroids is not None
            scat.set_visible(visibility)

            if visibility and s_centroids is not None:
                s_ys = s_centroids[i, 1]
                s_xs = s_centroids[i, 0]
                scat.set_offsets(np.column_stack((s_xs, s_ys)))

        # concept text:
        limite = self.dataset.get_global_limits()
        plot_range = limite[1] - limite[0]
        proximity_threshold = 0.06 * plot_range  # threshold de 6% do range do gráfico
        placed_positions = []
        
        # 8 direções ordenadas de offset para resolver colisões de forma uniforme
        offsets = [
            (0.0, 0.12),    # Acima
            (0.0, -0.22),   # Abaixo
            (0.18, -0.05),  # Direita
            (-0.18, -0.05), # Esquerda
            (0.13, 0.13),   # Superior Direito
            (-0.13, -0.18), # Inferior Esquerdo
            (0.13, -0.18),  # Inferior Direito
            (-0.13, 0.13)   # Superior Esquerdo
        ]

        for i, txt in enumerate(self.concept_labels):
            # A visibilidade do texto segue a visibilidade do conceito
            # e a escolha do usuário de ver nomes
            visibility = self.concept_visibility[i].get() and (destaque or self.s_mean_view.get())
            if self.s_mean_view.get() and s_centroids is None:
                visibility = False
            txt.set_visible(visibility)

            if visibility:
                # 1. Define o que será escrito (o nome genérico do conceito)
                generic_name = self.dataset.concept_mapping.get(self.dataset.headers[i], f"C{i+1}")
                txt.set_text(generic_name)

                # 2. Define a posição baseada no modo de visualização
                if self.s_mean_view.get() and s_centroids is not None:
                    # Texto em cima da média dos alunos
                    x, y = s_centroids[i, 0], s_centroids[i, 1]
                else:
                    # Texto em cima do ponto do participante em destaque
                    x, y = curr_mds[0, i, 0], curr_mds[0, i, 1]

                # 3. Resolve colisões aplicando direções alternadas de offset
                collision_count = 0
                for px, py in placed_positions:
                    if np.sqrt((x - px)**2 + (y - py)**2) < proximity_threshold:
                        collision_count += 1
                
                offset_idx = collision_count % len(offsets)
                dx, dy = offsets[offset_idx]
                
                # Escala o offset proporcionalmente ao tamanho (limites) do gráfico
                scaled_dx = dx * (plot_range / 10.0)
                scaled_dy = dy * (plot_range / 10.0)

                txt.set_position((x + scaled_dx, y + scaled_dy))
                placed_positions.append((x, y))

        for i, ellipse in enumerate(self.ellipses):
            visibility = self.concept_visibility[i].get() and self.ellipses_view.get() and s_centroids is not None and s_stds is not None
            ellipse.set_visible(visibility)

            if visibility and s_centroids is not None and s_stds is not None:
                # set ellipse center:
                center = (s_centroids[i, 0], s_centroids[i, 1])
                ellipse.set_center(center)

                # set ellipse dim:
                ellipse.set_width(s_stds[i, 0] * 4)
                ellipse.set_height(s_stds[i, 1] * 4)

        segmentos = []

        for i in range(self.num_concepts):
            # Só calculamos a linha se o conceito estiver visível no Checkbox
            if self.concept_visibility[i].get():

                # Ponto de Origem: Sempre a Média dos Professores (se estiver ativa)
                if mean and p_centroids is not None:
                    pos_prof = p_centroids[i]

                    # Destino 1: Ponto do Participante (se não estiver em modo "apenas médias")
                    if not self.s_mean_view.get():
                        # curr_mds tem len = len(ranked_indices) ou 1
                        pos_dest = curr_mds[0, i] if not dispersion else self.mds_results[self.id, i]
                        segmentos.append([pos_prof, pos_dest])

                    # Destino 2: Média dos Estudantes (se estiver ativa)
                    if self.s_mean_view.get() and s_centroids is not None:
                        pos_stud = s_centroids[i]
                        segmentos.append([pos_prof, pos_stud])

        # Atualiza as linhas de uma vez só
        self.connection_lines.set_segments(segmentos)

        # Define a visibilidade da coleção (só aparece se houver algo para ligar)
        self.connection_lines.set_visible(len(segmentos) > 0)
        
        # Evolution lines
        show_evo = self.evo_view_values.get()
        if show_evo and self.phase == "pos":
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
                            evo_segs.append([self.mds_results_pre[self.id, i], self.mds_results_pos[self.id, i]])
            
            self.evo_lines.set_segments(evo_segs)
            self.evo_lines.set_visible(len(evo_segs) > 0)
        else:
            self.evo_lines.set_segments([])
            self.evo_lines.set_visible(False)

        # set alpha 1.0 in destaque participant, and 0.1 to the others:
        # if dispersion:

        for i, scat in enumerate(self.scatters):
            # pega cor base do scat:
            face_color = scat.get_facecolor()[0]

            # cria um vetor novo de cores, com a cor base na opacidade 1.0:
            new_colors = np.tile(face_color, (len(curr_mds), 1))
            # deixa todas as cores com 0.1 de opacidade:
            new_colors[:, 3] = 0.1
            # retorna apenas o participante em destaque para a opacidade 1.0:
            if destaque:
                if dispersion:
                    try:
                        highlight_idx = ranked_indices.index(self.id)
                        new_colors[highlight_idx, 3] = 1.0
                    except ValueError:
                        pass
                else:
                    new_colors[0, 3] = 1.0

            scat.set_facecolor(new_colors)
            scat.set_edgecolor(new_colors)

        self.canvas.draw_idle()

        self.ax.set_xlabel("Dimensão 1")
        self.ax.set_ylabel("Dimensão 2")
        self.ax.grid(True, linestyle='--', alpha=0.5)

        # Aplica limites fixos baseados no dataset global
        limite = self.dataset.get_global_limits()  # Supondo que você tenha acesso ao dataset aqui
        self.ax.set_xlim(limite)
        self.ax.set_ylim(limite)

        # Garante que 1 unidade no eixo X tenha o mesmo tamanho físico que 1 unidade no Y
        self.ax.set_aspect('equal')
        self.canvas.draw()

    def get_ranked_indices(self, p_centroids):
        mode = self.ranking_mode_var.get()
        try:
            n = self.ranking_n_var.get()
        except tk.TclError:
            n = 5 # Valor de fallback seguro caso a caixa fique vazia temporariamente
            
        num_students = len(self.mds_results)
        all_indices = list(range(num_students))
        
        if mode == "Todos os Alunos" or p_centroids is None:
            return all_indices
            
        distances = []
        if mode in ["Top Alinhados", "Top Divergentes"]:
            for j in range(num_students):
                dist = np.sum(np.linalg.norm(self.mds_results[j] - p_centroids, axis=1))
                distances.append(dist)
                
            sorted_indices = np.argsort(distances)
            if mode == "Top Divergentes":
                sorted_indices = sorted_indices[::-1]
            return sorted_indices[:n].tolist()
            
        elif mode == "Top Evolução":
            if self.mds_results_pre is None or self.mds_results_pos is None:
                return all_indices
                
            for j in range(num_students):
                dist_pre = np.sum(np.linalg.norm(self.mds_results_pre[j] - p_centroids, axis=1))
                dist_pos = np.sum(np.linalg.norm(self.mds_results_pos[j] - p_centroids, axis=1))
                distances.append(dist_pre - dist_pos)
                
            sorted_indices = np.argsort(distances)[::-1]
            return sorted_indices[:n].tolist()

    def get_all_participants(self) -> list:
        if not self.dataset or not self.dataset.participants:
            return []
        p_list = self.dataset.participants.get("professors", [])
        s_list = self.dataset.participants.get("students", [])
        return (p_list or []) + (s_list or [])

    # calls highlight method of visualization area:
    def _hightlight_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        headers = self.dataset.selected_headers
        participants = self.get_all_participants()
        if not participants or idx >= len(participants):
            return

        self.selected_participant = participants[idx]
        self.show_matrix(headers)
        self.show_mds()

    # calls destaque method of visualization area:
    def _destaque_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        headers = self.dataset.selected_headers
        participants = self.get_all_participants()
        if not participants or idx >= len(participants):
            return

        self.selected_participant = participants[idx]
        self.show_matrix(headers)
        self.show_mds()

    # calls mean_view method of visualization area:
    def _mean_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.get_all_participants()
        if not participants or idx >= len(participants):
            return

        self.selected_participant = participants[idx]
        self.show_mds()

    # calls dispersion_view method of visualization area:
    def _dispersion_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.get_all_participants()
        if not participants or idx >= len(participants):
            return

        self.selected_participant = participants[idx]
        self.show_mds()

    # calls ellipse_view method of visualization area:
    def _ellipse_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.get_all_participants()
        if not participants or idx >= len(participants):
            return

        self.selected_participant = participants[idx]
        self.show_mds()

    # calls evo_view method of visualization area:
    def _evo_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.get_all_participants()
        if not participants or idx >= len(participants):
            return

        self.selected_participant = participants[idx]
        self.show_mds()

    def atualizar_estado_ranking(self):
        if not hasattr(self, "ranking_spin") or not self.ranking_spin:
            return
        # Verifica o valor selecionado no Combobox
        if self.ranking_mode_var.get() == "Todos os Alunos":
            # Desabilita o Spinbox e muda a cor do Label para parecer desativado
            self.ranking_spin.config(state="disabled")
            self.quantidade_label.config(foreground="gray")
        else:
            # Reabilita o Spinbox e volta a cor do Label ao normal
            self.ranking_spin.config(state="normal")
            self.quantidade_label.config(foreground="")

        # Executa a sua função original de atualizar os dados na tela
        self.show_mds()

    #
    def set_index(self, idx: int, phase: str = "pre", status: str = "default") -> None:
        self.id = idx
        self.phase = phase

        if status == "default":
            self.s_mean_view.set(False)
            self.destaque_view_values.set(True)
            self.destaque_view_checkbox.state(['!alternate', '!disabled'])
        if status == "mean":
            self.s_mean_view.set(True)
            self.destaque_view_values.set(False)
            self.destaque_view_checkbox.state(['alternate', 'disabled'])

        if phase == "pre":
            self.evo_view_checkbox.state(['alternate', 'disabled'])
            self.ranking_combo["values"] = ["Todos os Alunos", "Top Alinhados", "Top Divergentes"]
            if self.ranking_mode_var.get() == "Top Evolução":
                self.ranking_mode_var.set("Todos os Alunos")
                self.atualizar_estado_ranking()
        if phase == "pos":
            self.evo_view_checkbox.state(['!alternate', '!disabled'])
            self.ranking_combo["values"] = ["Todos os Alunos", "Top Alinhados", "Top Divergentes", "Top Evolução"]

        self.refresh()

    #
    @staticmethod
    def value_to_color(df: pd.DataFrame, r: int, c: int) -> str:
        v = df.iloc[r, c]

        if v == 0:
            cor = "#96C8FF"
        elif v <= 1:
            cor = "#96FFE1"
        elif v <= 2:
            cor = "#64FF96"
        elif v <= 3:
            cor = "#C8FF7D"
        elif v <= 4:
            cor = "#FFFF64"
        elif v <= 5:
            cor = "#FFC832"
        elif v <= 6:
            cor = "#FF9632"
        elif v <= 7:
            cor = "#FF7D64"
        elif v <= 8:
            cor = "#FF644B"
        elif v <= 9:
            cor = "#FF3232"
        else :
            cor = "#FFFFFF"

        return cor

    #
    def get_current_tab(self) -> None:
        notebook = self.notebook
        tab = notebook.tab(notebook.select(), "text")

        unicoded_name = unicode_text(tab)
        treated_name = unicoded_name.lower().replace(" ", "_")
        self.curr_view = treated_name

    def select_all(self):
        for visibility in self.concept_visibility:
            visibility.set(self.all_selection_values.get())

        self.refresh()

    def set_mode(self, mode: str) -> None:
        self.dataset_mode = mode
        
        # Ocultar ou mostrar o painel de controle lateral do MDS e os botões
        if mode == "group":
            if hasattr(self, "mds_view") and self.mds_view and hasattr(self, "mds_ctrl") and self.mds_ctrl:
                if self.mds_ctrl not in self.mds_view.panes():
                    self.mds_view.add(self.mds_ctrl, minsize=100, stretch="never")
            
            if hasattr(self, "mean_view_checkbox") and self.mean_view_checkbox:
                self.mean_view_checkbox.pack(fill="x", padx=10)
            if hasattr(self, "dispersion_view_checkbox") and self.dispersion_view_checkbox:
                self.dispersion_view_checkbox.pack(fill="x", padx=10)
            if hasattr(self, "ellipse_view_checkbox") and self.ellipse_view_checkbox:
                self.ellipse_view_checkbox.pack(fill="x", padx=10)
            if hasattr(self, "evo_view_checkbox") and self.evo_view_checkbox:
                self.evo_view_checkbox.pack(fill="x", padx=10)
            if hasattr(self, "ranking_frame") and self.ranking_frame:
                self.ranking_frame.pack(fill="x", padx=10, pady=5)
        else:
            if hasattr(self, "mds_view") and self.mds_view and hasattr(self, "mds_ctrl") and self.mds_ctrl:
                if self.mds_ctrl in self.mds_view.panes():
                    self.mds_view.forget(self.mds_ctrl)

            if hasattr(self, "mean_view_checkbox") and self.mean_view_checkbox:
                self.mean_view_checkbox.pack_forget()
            if hasattr(self, "dispersion_view_checkbox") and self.dispersion_view_checkbox:
                self.dispersion_view_checkbox.pack_forget()
            if hasattr(self, "ellipse_view_checkbox") and self.ellipse_view_checkbox:
                self.ellipse_view_checkbox.pack_forget()
            if hasattr(self, "evo_view_checkbox") and self.evo_view_checkbox:
                self.evo_view_checkbox.pack_forget()
            if hasattr(self, "ranking_frame") and self.ranking_frame:
                self.ranking_frame.pack_forget()

        # Recriar abas e limpar dados velhos de acordo com o modo
        self.id = 0
        self.refresh()

    def on_cell_edited(self, event) -> None:
        try:
            # Desempacota as informações do evento de edição do tksheet
            row, col, value_before, value_after, *rest = event
        except Exception:
            print("Deu não")
            return

        # Impedir edições na diagonal ou triângulo superior
        if row <= col:
            if row == col:
                self.sheet.set_cell_data(row, col, 0.0)
            else:
                # Restaura o valor espelhado do triângulo inferior
                lower_val = self.sheet.get_cell_data(col, row)
                self.sheet.set_cell_data(row, col, lower_val)
            return

        # Tratar valor numérico
        try:
            if value_after == "-" or value_after == "" or value_after is None:
                val_num = np.nan
            else:
                val_num = float(value_after)
        except ValueError:
            # Reverte a edição na planilha caso o valor não seja conversível
            self.sheet.set_cell_data(row, col, value_before)
            return

        # Atualiza o espelhamento simétrico na planilha no triângulo superior
        self.sheet.set_cell_data(col, row, val_num)

        # Atualiza no dataset
        actual_phase = "pos" if self.phase == "pos" else "pre"
        
        if self.dataset_mode == "single":
            if not self.dataset.participants or not self.dataset.participants.get("students"):
                return
            p = self.dataset.participants["students"][0]
        else:
            if not self.dataset.participants or not self.dataset.participants.get("students") or self.id is None:
                return
            p = self.dataset.participants["students"][self.id]

        df = getattr(p, f"dataframe_{actual_phase}")
        if df is not None:
            header_r = self.dataset.headers[row]
            header_c = self.dataset.headers[col]
            df.at[header_r, header_c] = val_num
            df.at[header_c, header_r] = val_num
            getattr(p, f"mds_result_{actual_phase}").fit(df)

        self.dataset.calc_mean()

        # Redesenha a planilha (mantendo coloração e novidades) e re-plota o MDS
        self.show_matrix(self.dataset.headers)
        self.show_mds()

    def on_select_cell(self, event) -> None:
        print(event)
        try:
            row, col = event[0], event[1]
        except Exception:
            return

        if not self.dataset or not self.dataset.headers:
            return

        num = len(self.dataset.headers)
        editable_cells = [(r, c) for r in range(num) for c in range(num) if r > c]
        if not editable_cells:
            return

        # Se for uma célula editável, atualiza prev_cell e sai
        if row > col:
            self.prev_cell = (row, col)
            return

        # Célula bloqueada. Precisamos pular.
        if not hasattr(self, "prev_cell") or self.prev_cell is None:
            self.prev_cell = editable_cells[0]

        r_prev, c_prev = self.prev_cell
        
        try:
            i_prev = editable_cells.index((r_prev, c_prev))
        except ValueError:
            i_prev = 0

        # Determinar a direção do movimento
        if row > r_prev and col == c_prev:
            # Movimento para Baixo (Enter/Down) -> Procurar na mesma coluna
            found = False
            for r in range(row, num):
                if r > col:
                    self.sheet.select_cell(r, col)
                    self.sheet.see(r, col, keep_selection=True)
                    self.prev_cell = (r, col)
                    found = True
                    break
            if not found:
                for r in range(0, row):
                    if r > col:
                        self.sheet.select_cell(r, col)
                        self.sheet.see(r, col, keep_selection=True)
                        self.prev_cell = (r, col)
                        break
                        
        elif row < r_prev and col == c_prev:
            # Movimento para Cima (Up) -> Procurar na mesma coluna subindo
            found = False
            for r in range(row, -1, -1):
                if r > col:
                    self.sheet.select_cell(r, col)
                    self.sheet.see(r, col, keep_selection=True)
                    self.prev_cell = (r, col)
                    found = True
                    break
            if not found:
                for r in range(num - 1, row, -1):
                    if r > col:
                        self.sheet.select_cell(r, col)
                        self.sheet.see(r, col, keep_selection=True)
                        self.prev_cell = (r, col)
                        break
                        
        elif col < c_prev or (row < r_prev and c_prev == 0):
            # Movimento para Trás (Shift-Tab / Left) -> Ir para o editável anterior na lista
            next_idx = (i_prev - 1) % len(editable_cells)
            r_next, c_next = editable_cells[next_idx]
            self.sheet.select_cell(r_next, c_next)
            self.sheet.see(r_next, c_next, keep_selection=True)
            self.prev_cell = (r_next, c_next)
            
        else:
            # Movimento para Frente (Tab / Right) -> Ir para o próximo editável na lista
            next_idx = (i_prev + 1) % len(editable_cells)
            r_next, c_next = editable_cells[next_idx]
            self.sheet.select_cell(r_next, c_next)
            self.sheet.see(r_next, c_next, keep_selection=True)
            self.prev_cell = (r_next, c_next)