import numpy as np
import tkinter as tk
from tkinter import ttk
from tksheet import Sheet


class VisualizationArea(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.sheet = None
        self._create_widgets()

    # create the visualization area (notebook):
    def _create_widgets(self):
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # notebook:
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
    def show_dataframe(self, dataset, index=0):
        # ----------------------------------------------------------------------
        # clear layout:
        # ----------------------------------------------------------------------

        # clear all tabs:
        for tab in self.notebook.tabs():
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

    # configure and stilyze data placement:
    def show_matrix(self, data, headers, highlight=False):
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
        df = data["df"].loc[headers, headers]
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

    @staticmethod
    def value_to_color(df, r, c):
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
