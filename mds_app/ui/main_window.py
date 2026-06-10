import tkinter as tk
from tkinter import ttk

from mds_app.data.dataset import Dataset
from mds_app.ui.toolbar import ToolBar
from mds_app.ui.control_panel import ControlPanel
from mds_app.ui.visualization_area import VisualizationArea


class MainWindow:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Analisador MDS Educacional")
        self.root.geometry("1080x720")

        self.dataset_group = Dataset()
        self.dataset_single = Dataset()
        self.dataset = self.dataset_group
        self.current_mode = "group"

        self._create_layout()

    # create all main window layout:
    def _create_layout(self) -> None:
        # main PanedWindow (horizontal):
        self.main_paned = tk.PanedWindow(self.root, orient="horizontal")

        # Instanciar elementos do modo de grupo de forma isolada
        self.visualization_area_group = VisualizationArea(self.main_paned, self.dataset_group, mode="group")
        self.control_panel_group = ControlPanel(self.main_paned, self.dataset_group, self.visualization_area_group, mode="group")

        # Instanciar elementos do modo específico de forma isolada
        self.visualization_area_single = VisualizationArea(self.main_paned, self.dataset_single, mode="single")
        self.control_panel_single = ControlPanel(self.main_paned, self.dataset_single, self.visualization_area_single, mode="single")

        # Referências ativas no momento inicial (grupo)
        self.control_panel = self.control_panel_group
        self.visualization_area = self.visualization_area_group

        # toolbar:
        self.toolbar = ToolBar(
            self.root,
            self.dataset,
            self.control_panel,
            self.visualization_area
        )
        self.toolbar.dataset_mode = self.current_mode
        self.toolbar.main_window = self  # Referência de volta para MainWindow

        # configure event binds:
        '''...'''

        # Adicionar apenas os painéis do modo de grupo inicialmente
        self.main_paned.add(self.control_panel_group, minsize=100)
        self.main_paned.add(self.visualization_area_group, minsize=100)

        self.root.update_idletasks()
        self.main_paned.sash_place(0, 300, 0)

        self.toolbar.pack(side="top", fill="x")
        self.toolbar.pack_propagate(False)
        self.main_paned.pack(fill="both", expand=True)

    def set_mode(self, mode: str) -> None:
        if mode == self.current_mode:
            return

        old_mode = self.current_mode
        self.current_mode = mode

        # Esquecer os painéis do modo antigo da PanedWindow
        if old_mode == "group":
            self.main_paned.forget(self.control_panel_group)
            self.main_paned.forget(self.visualization_area_group)
        else:
            self.main_paned.forget(self.control_panel_single)
            self.main_paned.forget(self.visualization_area_single)

        # Atualizar referências de dados
        if mode == "group":
            self.dataset = self.dataset_group
            self.control_panel = self.control_panel_group
            self.visualization_area = self.visualization_area_group
        else:
            self.dataset = self.dataset_single
            self.control_panel = self.control_panel_single
            self.visualization_area = self.visualization_area_single

        # Adicionar os painéis do modo novo
        self.main_paned.add(self.control_panel, minsize=100)
        self.main_paned.add(self.visualization_area, minsize=100)
        
        self.root.update_idletasks()
        self.main_paned.sash_place(0, 300, 0)

        # Atualizar a toolbar com referências do modo novo
        self.toolbar.dataset = self.dataset
        self.toolbar.control_panel = self.control_panel
        self.toolbar.visualization_area = self.visualization_area
        self.toolbar.dataset_mode = mode

        # Notificar os componentes
        self.control_panel.refresh()
        self.visualization_area.refresh()
        self.toolbar.set_mode(mode)

