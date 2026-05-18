import tkinter as tk
from tkinter import ttk, messagebox

from pandas.conftest import index
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
    def __init__(self, parent, dataset) -> None:
        super().__init__(parent)

        self.dataset: Dataset = dataset
        self.sheet: Sheet | None            = None
        self.notebook: ttk.Notebook | None  = None
        # self.mds_session = None

        self.id: int | None = None
        self.phase: str = "pre"
        self.curr_view = None

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

        self.data_view.add(self.data_content, minsize=100)
        self.data_view.add(self.data_ctrl, minsize=100)
        self.data_view.update_idletasks()
        self.data_view.sash_place(0, self.data_view.winfo_width() - 200, 0)

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
            # "all"
            "single_select",    # simple select
            "row_select",               # enable row selection
            "column_select",            # enable column selection
            "drag_select",
            "arrowkeys",
            "row_height_resize",
            # "row_width_  resize",
            "column_width_resize",
            # "column_height_resize",
            "double_click_column_resize",
            "double_click_row_resize",
            # "right_click_popup_menu",
            "rc_select",
            # "rc_insert_row",
            # "rc_delete_row",
            # "copy",
            # "paste",
            # "delete"
        )

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

        self.mds_view.add(self.mds_content, minsize=100)
        self.mds_view.add(self.mds_ctrl, minsize=100)
        self.mds_view.update_idletasks()
        self.mds_view.sash_place(0, self.mds_view.winfo_width() - 200, 0)

        ttk.Label(self.mds_content, text="Configuração da Análise",
                  font=("Arial", 12, "bold")).pack(pady=10)

        # Área de visualização

        # Criando Figure do plot:
        self.fig, self.ax = plt.subplots(figsize=(6, 6))

        self.canvas = FigureCanvasTkAgg(self.fig, self.mds_content)

        self.nav_toolbar = NavigationToolbar2Tk(self.canvas, self.mds_content)
        self.nav_toolbar.update()

        # ==================================================
        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        # participant = participants[self.id]

        self.num_concepts = len(self.dataset.headers)
        self.num_participants = len(participants)
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

        self.all_selection_checkbox = ttk.Checkbutton(
            ctrl_frame,
            text="Selecionar Tudo",
            variable=self.all_selection_values,
            command=self.select_all
        )
        self.all_selection_checkbox.pack(side="top", padx=5, anchor='w')

        for i in range(self.num_concepts):
            header = self.dataset.headers[i]
            btn = ttk.Checkbutton(
                ctrl_frame,
                text=header,
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

        self.canvas.get_tk_widget().pack(fill="both")
        self.nav_toolbar.pack()

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
                va='bottom',  # Alinhamento vertical: abaixo do ponto (o texto fica em cima)
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

    #
    def refresh(self):
        index = self.id
        dataset = self.dataset
        participant = dataset.participants["students"][index]
        header = dataset.headers

        self.show_matrix(header)
        self.show_mds()

    #
    def show_matrix(self, headers: list[str]) -> None:
        highlight = self.highlight_values.get()

        if not self.dataset:
            return

        p_participants = self.dataset.participants["professors"]
        s_participants = self.dataset.participants["students"]
        participants = p_participants + s_participants
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
            df = participant_df.loc[headers, headers]
        # headers = headers
        # print(headers)
        self.sheet.headers(headers)

        row_index = list(df.index.astype(str))
        self.sheet.row_index(row_index)

        # -----------------------------
        # insert (and style) data:
        # -----------------------------
        dados = df.values.tolist()
        self.sheet.set_sheet_data(dados)

        # clear style:
        self.sheet.dehighlight_all()

        for r in range(len(dados)):
            for c in range(len(dados[r])):
                if not highlight:   # default style
                    cor = "#f0f0f0" if r % 2 == 0 else "#ffffff"
                else:               # highlight style
                    cor = self.value_to_color(df, r, c)

                self.sheet.highlight_cells(
                    row=r,
                    column=c,
                    bg=cor,
                    fg="black",
                )

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
        p_participants = self.dataset.participants["professors"]
        s_participants = self.dataset.participants["students"]
        participants = p_participants + s_participants

        def get_valid_mds(p_list, ph):
            res = []
            for p in p_list:
                mds = getattr(p, f"mds_result_{ph}")
                if mds and mds.X_aligned is not None:
                    res.append(mds.X_aligned)
                else:
                    res.append(p.mds_result_pre.X_aligned)
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
        s_centroids = s_centr_ref.copy() if s_centr_ref is not None else None
        p_stds = p_stds_ref.copy() if p_stds_ref is not None else None
        s_stds = s_stds_ref.copy() if s_stds_ref is not None else None

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
            curr_mds = self.mds_results
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
        for i, txt in enumerate(self.concept_labels):
            # A visibilidade do texto segue a visibilidade do conceito
            # e a escolha do usuário de ver nomes
            visibility = self.concept_visibility[i].get() and (destaque or self.s_mean_view.get())
            if self.s_mean_view.get() and s_centroids is None:
                visibility = False
            txt.set_visible(visibility)

            if visibility:
                # 1. Define o que será escrito (o nome do conceito vindo do header)
                txt.set_text(self.dataset.headers[i])

                # 2. Define a posição baseada no modo de visualização
                if self.s_mean_view.get() and s_centroids is not None:
                    # Texto em cima da média dos alunos
                    x, y = s_centroids[i, 0], s_centroids[i, 1]
                else:
                    # Texto em cima do ponto do participante em destaque
                    # (Assumindo que em modo destaque o ponto principal está no índice 'index')
                    x, y = curr_mds[0, i, 0], curr_mds[0, i, 1]

                # 3. Aplica a nova posição com um pequeno offset em Y para não sobrepor o ponto
                txt.set_position((x, y + 0.1))

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
                        # curr_mds pode ter 1 ou N participantes (se for dispersão)
                        # Vamos ligar o participante atual (index 0 ou o específico)
                        pos_dest = curr_mds[0, i] if not dispersion else curr_mds[self.id, i]
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
                            for j in range(len(self.mds_results_pre)):
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
                    new_colors[self.id, 3] = 1.0
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

    #
    def enable_ctrl(self, status, phase):
        if status == "default":
            self.s_mean_view.set(False)
            self.destaque_view_values.set(True)
            self.destaque_view_checkbox.state(['!alternate', '!disabled'])
        if status == "mean":
            self.s_mean_view.set(True)
            self.destaque_view_values.set(False)
            self.destaque_view_checkbox.state(['alternate', 'disabled'])

        if phase == "pre":
            self.evo_view_checkbox.state(['!alternate', '!disabled'])
        if phase == "pos":
            self.evo_view_checkbox.state(['alternate', 'disabled'])

    # calls highlight method of visualization area:
    def _hightlight_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        headers = self.dataset.selected_headers

        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        self.selected_participant = participants[idx]
        self.show_matrix(headers)
        self.show_mds()

    # calls destaque method of visualization area:
    def _destaque_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        headers = self.dataset.selected_headers

        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        self.selected_participant = participants[idx]
        self.show_matrix(headers)
        self.show_mds()

    # calls mean_view method of visualization area:
    def _mean_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        self.selected_participant = participants[idx]
        self.show_mds()

    # calls dispersion_view method of visualization area:
    def _dispersion_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        self.selected_participant = participants[idx]
        self.show_mds()

    # calls ellipse_view method of visualization area:
    def _ellipse_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        self.selected_participant = participants[idx]
        self.show_mds()

    # calls evo_view method of visualization area:
    def _evo_view_values(self) -> None:
        idx = self.id
        if idx is None:
            return

        participants = self.dataset.participants["professors"] + self.dataset.participants["students"]
        self.selected_participant = participants[idx]
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
        if phase == "pos":
            self.evo_view_checkbox.state(['!alternate', '!disabled'])

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