import tkinter as tk
from tkinter import ttk

from mds_app.analysis.mds_engine import MDSEngine
from mds_app.data.dataset import Dataset
from mds_app.ui.menubar import MenuBar
from mds_app.ui.toolbar import ToolBar
from mds_app.ui.control_panel import ControlPanel
from mds_app.ui.visualization_area import VisualizationArea


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Analisador MDS Educacional")
        self.root.geometry("900x600")

        self._create_layout()

    # create all main window layout:
    def _create_layout(self) -> None:
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # main PanedWindow (horizontal):
        self.main_paned = tk.PanedWindow(self.root, orient="horizontal")

        # ----------------------------------------------------------------------
        # initialing custom widgets:
        # ----------------------------------------------------------------------

        # dataset:
        self.dataset = Dataset()

        # visualization_area:
        self.visualization_area = VisualizationArea(self.main_paned)

        # control panel:
        self.control_panel = ControlPanel(
            self.main_paned,
            self.dataset,
            self.visualization_area
        )

        # menubar:
        self.menubar = MenuBar(
            self.root,
            self.dataset,
            self.control_panel,
            self.visualization_area,
        )

        # toolbar:
        self.toolbar = ToolBar(
            self.root,
            self.dataset,
            self.control_panel,
            self.visualization_area
        )

        # ----------------------------------------------------------------------
        # configure event binds:
        # ----------------------------------------------------------------------
        '''...'''

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------

        # adding widgets in panedWindow:
        self.main_paned.add(self.control_panel, minsize=100)
        self.main_paned.add(self.visualization_area, minsize=100)

        self.root.update_idletasks()
        self.main_paned.sash_place(0, 200, 0)
        # self.main_paned.configure(sashwidth=20)

        self.root.configure(menu=self.menubar)  # adding menubar

        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)
        self.main_paned.pack(fill="both", expand=True)

        # ----------------------------------------------------------------------
        # :
        # ----------------------------------------------------------------------
        # self.control_panel.refresh()

