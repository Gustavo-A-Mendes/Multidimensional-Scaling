import tkinter as tk
from tkinter import ttk, messagebox
from tksheet import Sheet

import numpy as np
import pandas as pd
from matplotlib.collections import PathCollection
from matplotlib.patches import Ellipse

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant

class VisualizationArea(ttk.Frame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.sheet: Sheet | None            = None
        self.notebook: ttk.Notebook | None  = None
        self.mds_session = None

        self.id: int | None = None
        self.destaque = None
        self.mean = None
        self.dispersion = None

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

    # plot dataframe in visualization area:
    def create_dataframe(self, dataset: Dataset, index: int = 0) -> None:
        # ----------------------------------------------------------------------
        # clear layout:
        # ----------------------------------------------------------------------

        # clear data tabs:
        tabs = self.notebook.tabs()
        for tab in tabs:
            if self.notebook.tab(tab, "text") not in ("Início"):
                self.notebook.forget(tab)

        participant = dataset.participants[index]
        headers = dataset.selected_headers

        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # notebook tab:
        tab = ttk.Frame(self.notebook)
        # self.notebook.add(tab, text=f"{participant["name"]}{len(self.notebook.tabs())}")

        # sheet
        self.sheet = Sheet(
            tab,
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

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------
        self.notebook.add(tab, text=f"Dados")
        self.notebook.select(tab)
        self.sheet.pack(fill="both", expand=True)

        # placing data:
        self.show_matrix(participant, headers)

    #
    def create_mds(self, dataset: Dataset, tags: list[tk.BooleanVar], index: int = 0) -> None:
        # the dataset must not be empty:
        if not dataset.participants:
            messagebox.showerror(
                "Erro", "Dados não encontrados."
            )
            return

        # it will create two tabs: MDS_config and MDS_result:

        # clear MDS tabs:
        notebook = self.notebook
        tabs = notebook.tabs()
        for tab in tabs:
            if notebook.tab(tab, "text") in ("MDS_config", "MDS_result"):
                notebook.forget(tab)

        mds_config_tab = ttk.Frame(notebook)
        mds_result_tab = ttk.Frame(notebook)

        notebook.add(mds_config_tab, text="MDS_config")
        notebook.add(mds_result_tab, text="MDS_result")

        notebook.select(mds_config_tab)

        # self.parent.control_panel.view = "mds_view"
        # self.parent.control_panel.refresh()

        main = ttk.Frame(mds_config_tab)
        main.pack(fill="both", expand=True)

        ttk.Label(main, text="Configuração da Análise",
                  font=("Arial", 12, "bold")).pack(pady=10)

        # Área de visualização
        self.view = ttk.Frame(main)
        self.view.pack(pady=10)

        # Criando Figure do plot:
        self.mds_plot = ttk.Frame(self.view)
        self.mds_plot.pack(fill="both", expand=True)

        self.fig, self.ax = plt.subplots(figsize=(6, 6))

        self.canvas = FigureCanvasTkAgg(self.fig, self.mds_plot)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.nav_toolbar = NavigationToolbar2Tk(self.canvas, self.mds_plot)
        self.nav_toolbar.update()
        self.nav_toolbar.pack()

        self.show_mds(dataset, dataset.participants[index], tags, index)
        # self.show_group_mds(dataset)

    # configure and stilyze data placement:
    def show_matrix(self, data: Participant, headers: list[str], highlight: bool = False) -> None:
        if not data:
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
        df = data.dataframe.loc[headers, headers]
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
    def show_mds(self, data: Dataset, participant: Participant, tags: list[tk.BooleanVar], index: int = 0) -> None:
        mds_results = [p.mds_result for p in data.participants]
        centroids   = data.centroids.copy()
        stds        = data.stds.copy()

        highlight   = tags[0].get()
        destaque    = tags[1].get()
        mean        = tags[2].get()
        dispersion  = tags[3].get()

        # 1. Definir um mapa de cores (ex: 'tab10', 'Set3' ou 'hsv')
        # O 'tab10' é ótimo para até 10 categorias com cores bem distintas
        cmap = plt.get_cmap('tab10')

        # # Limpa o gráfico existente:
        # self.ax.clear()

        if destaque and not self.destaque:
            participant_mds = participant.mds_result

            # adiciona novos dados:
            xs = []
            ys = []
            colors = []
            labels = participant_mds.labels.copy()

            for i, (x, y) in enumerate(participant_mds.X_aligned):
                # Definindo a cor para este conceito específico
                # Usamos o resto da divisão (%) caso existam mais conceitos que cores no mapa
                color = cmap(i % 10)

                # for (x, y) in mds_result.X:
                xs.append(x)
                ys.append(y)
                colors.append(color)


            # centróides em um único scatter
            scatter = self.ax.scatter(xs, ys, c=colors)

            texts = []
            for i, label in enumerate(labels):
                text = self.ax.text(xs[i], ys[i], label)
                texts.append(text)

            title = self.ax.set_title(f"MDS (Stress: {participant_mds.stress})")

            #
            destaque_artists = {
                "scatter": scatter,
                'texts': texts,
                'title': title
            }

            self.destaque = destaque_artists.copy()

        if mean and not self.mean:
            # Assumimos que os labels são consistentes entre os participantes
            labels = data.participants[0].mds_result.labels

            # 3. Plota os centroides
            xs = centroids[:, 0]
            ys = centroids[:, 1]
            colors = []

            # 4. Desenha as elipses e labels
            for i in range(len(labels)):
                # Definindo a cor para este conceito específico
                # Usamos o resto da divisão (%) caso existam mais conceitos que cores no mapa
                color = cmap(i % 10)

                colors.append(color)

            #
            mean_artists = []

            # centróides em um único scatter
            # scatter = self.ax.scatter(xs, ys, c=colors, marker='X', s=80, label='Média da Turma')
            # mean_artists.append(scatter)

            # 4. Desenha as elipses e labels
            for i, label in enumerate(labels):
                # Definindo a cor para este conceito específico
                # Usamos o resto da divisão (%) caso existam mais conceitos que cores no mapa
                color = cmap(i % 10)

                # O desvio padrão define o raio. Multiplicamos por 4 para cobrir
                # aproximadamente 95% da dispersão (2 sigmas).
                width = stds[i, 0] * 4
                height = stds[i, 1] * 4

                # Criando a elipse de dispersão
                ellipse = Ellipse(
                    xy=(xs[i], ys[i]),
                    width=width,
                    height=height,
                    angle=0,  # MDS clássico não gera correlação rotacional intrínseca aqui
                    edgecolor=color,
                    facecolor='none',
                    linewidth=1.5,
                    alpha=0.60,  # Transparência para não poluir o gráfico
                    label='Dispersão' if i == 0 else ""
                )
                self.ax.add_patch(ellipse)
                mean_artists.append(ellipse)

                # # Plota o centróide com a mesma cor para manter a consistência
                # self.ax.scatter(xs[i], ys[i], color=color, marker='X', s=80, label='Média da Turma')

                # Label do conceito
                text = self.ax.text(xs[i] + (width / 4), ys[i] + (height / 4), label,
                             fontsize=9, fontweight='bold', color=color)
                mean_artists.append(text)

                # title = self.ax.set_title("Mapa Perceptual da Turma (Centroides e Dispersão)")
                # mean_artists.append(title)

            self.mean = mean_artists.copy()

        if dispersion and not self.dispersion:
            participant_mds = [p.mds_result for p in data.participants]

            # adiciona novos dados:
            xs = []
            ys = []
            colors = []

            for i, r in enumerate(participant_mds):
                for j, (x, y) in enumerate(r.X_aligned):
                    # Definindo a cor para este conceito específico
                    # Usamos o resto da divisão (%) caso existam mais conceitos que cores no mapa
                    color = cmap(j % 10)

                    # for (x, y) in mds_result.X:
                    xs.append(x)
                    ys.append(y)
                    colors.append(color)

            self.dispersion = self.ax.scatter(xs, ys, c=colors, alpha=0.10)

        if self.destaque and index != self.id:
            self.id = index

            participant_mds = data.participants[index].mds_result

            # adiciona novos dados:
            xs = []
            ys = []
            colors = []
            labels = participant_mds.labels.copy()

            for i, (x, y) in enumerate(participant_mds.X_aligned):
                # Definindo a cor para este conceito específico
                # Usamos o resto da divisão (%) caso existam mais conceitos que cores no mapa
                color = cmap(i % 10)

                # for (x, y) in mds_result.X:
                xs.append(x)
                ys.append(y)
                colors.append(color)

            self.destaque['scatter'].set_offsets(np.column_stack((xs, ys)))
            # self.destaque['scatter'].set_facecolor(colors)

            for i, text in enumerate(self.destaque["texts"]):
                text.set_position((xs[i], ys[i]))

            self.destaque["title"].set_text(f"MDS (Stress: {participant_mds.stress})")

        if self.destaque:
            self.destaque['scatter'].set_visible(destaque)

            if not mean:
                for artist in self.destaque["texts"]:
                    artist.set_visible(destaque)
            else:
                for artist in self.destaque["texts"]:
                    artist.set_visible(False)

            self.destaque['title'].set_visible(destaque)

        if self.mean:
            for artist in self.mean:
                artist.set_visible(mean)

        if self.dispersion:
            self.dispersion.set_visible(dispersion)


        self.ax.set_xlabel("Dimensão 1")
        self.ax.set_ylabel("Dimensão 2")
        self.ax.grid(True, linestyle='--', alpha=0.5)

        # Aplica limites fixos baseados no dataset global
        limite = data.get_global_limits()  # Supondo que você tenha acesso ao dataset aqui
        self.ax.set_xlim(limite)
        self.ax.set_ylim(limite)

        # Garante que 1 unidade no eixo X tenha o mesmo tamanho físico que 1 unidade no Y
        self.ax.set_aspect('equal')
        self.canvas.draw()

    #
    def show_group_mds(self, data: Dataset) -> None:
        """
        Plota os centroides da turma com elipses de dispersão baseadas no desvio padrão.
        """
        # 1. Limpa o gráfico existente
        self.ax.clear()

        # 2. Obtém os dados da classe Dataset
        centroids = data.centroids
        stds = data.stds
        # Assumimos que os labels são consistentes entre os participantes
        labels = data.participants[0].mds_result.labels

        # 3. Plota os centroides
        xs = centroids[:, 0]
        ys = centroids[:, 1]
        # self.ax.scatter(xs, ys, c=color, marker='X', s=80, label='Média da Turma')

        # 1. Definir um mapa de cores (ex: 'tab10', 'Set3' ou 'hsv')
        # O 'tab10' é ótimo para até 10 categorias com cores bem distintas
        cmap = plt.get_cmap('tab10')

        # 4. Desenha as elipses e labels
        for i, label in enumerate(labels):
            # Definindo a cor para este conceito específico
            # Usamos o resto da divisão (%) caso existam mais conceitos que cores no mapa
            color = cmap(i % 10)

            # O desvio padrão define o raio. Multiplicamos por 4 para cobrir
            # aproximadamente 95% da dispersão (2 sigmas).
            width = stds[i, 0] * 4
            height = stds[i, 1] * 4

            # Criando a elipse de dispersão
            ellipse = Ellipse(
                xy=(xs[i], ys[i]),
                width=width,
                height=height,
                angle=0,  # MDS clássico não gera correlação rotacional intrínseca aqui
                edgecolor=color,
                facecolor='none',
                linewidth=2,
                alpha=0.60,  # Transparência para não poluir o gráfico
                label='Dispersão' if i == 0 else ""
            )
            self.ax.add_patch(ellipse)


            # Plota o centróide com a mesma cor para manter a consistência
            self.ax.scatter(xs[i], ys[i], color=color, marker='X', s=80, label='Média da Turma')

            # Label do conceito
            self.ax.text(xs[i] + (width / 50), ys[i] + (height / 50), label,
                         fontsize=9, fontweight='bold', color='black')

        # 5. Configurações estéticas

        self.ax.set_title("Mapa Perceptual da Turma (Centroides e Dispersão)")
        self.ax.set_xlabel("Dimensão 1")
        self.ax.set_ylabel("Dimensão 2")
        self.ax.grid(True, linestyle='--', alpha=0.5)

        # Aplica limites fixos baseados no dataset global
        limite = data.get_global_limits()  # Supondo que você tenha acesso ao dataset aqui
        self.ax.set_xlim(limite)
        self.ax.set_ylim(limite)

        # Garante que 1 unidade no eixo X tenha o mesmo tamanho físico que 1 unidade no Y
        self.ax.set_aspect('equal')

        self.canvas.draw()

    #
    @staticmethod
    def value_to_color(df: pd.DataFrame, r: int, c: int) -> str:
        v = df.iloc[r, c]

        if v == 0:
            cor = "#96C8FF"
        elif v == 1:
            cor = "#96FFE1"
        elif v == 2:
            cor = "#64FF96"
        elif v == 3:
            cor = "#C8FF7D"
        elif v == 4:
            cor = "#FFFF64"
        elif v == 5:
            cor = "#FFC832"
        elif v == 6:
            cor = "#FF9632"
        elif v == 7:
            cor = "#FF7D64"
        elif v == 8:
            cor = "#FF644B"
        elif v == 9:
            cor = "#FF3232"
        else :
            cor = "#FFFFFF"

        return cor
