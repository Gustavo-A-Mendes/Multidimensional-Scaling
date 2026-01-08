import tkinter as tk
from tkinter import ttk

from data.dataset import Dataset
from ui.toolbar import ToolBar
from ui.control_panel import ControlPanel
from ui.visualization_area import VisualizationArea


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisador MDS Educacional")
        self.root.geometry("1200x800")

        self._create_layout()

    def _create_layout(self):
        # Paned principal (horizontal)
        self.main_paned = tk.PanedWindow(self.root, orient="horizontal")

        # Painel de controle
        self.control_panel = ControlPanel(self.main_paned)
        self.main_paned.add(self.control_panel, minsize=100)
        # self.main_paned.paneconfigure(self.control_panel, minsize=200)

        # Área de visualização
        self.visualization_area = VisualizationArea(self.main_paned)
        self.main_paned.add(self.visualization_area, minsize=100)

        # Barra de ferramentas
        self.dataset = Dataset()

        self.toolbar = ToolBar(
            self.root,
            self.dataset,
            self.visualization_area
        )


        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(0)
        self.main_paned.pack(fill="both", expand=True)
