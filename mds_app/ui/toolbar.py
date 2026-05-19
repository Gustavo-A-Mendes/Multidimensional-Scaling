from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from typing import Union, TYPE_CHECKING

from mds_app.ui.group_mapping_window import GroupMappingWindow
from mds_app.ui.import_dialog import ImportDialog
from mds_app.utils.csv_loader import *
from mds_app.utils.validators import *
from mds_app.ui.export_window import ExportWindow

# if TYPE_CHECKING:
from mds_app.ui.control_panel import ControlPanel
from mds_app.ui.visualization_area import VisualizationArea

class ToolBar(ttk.Frame):
    def __init__(self, parent, dataset: Dataset, control_panel: ControlPanel, visualization_area: VisualizationArea) -> None:
        super().__init__(parent)
        self.parent = parent
        self.dataset = dataset
        self.control_panel = control_panel
        self.visualization_area = visualization_area

        self._create_widgets()
        self.configure(height=100)

    # create the toolbar area:
    def _create_widgets(self) -> None:
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # button
        self.btn_import_pre = ttk.Button(
            self,
            text="Importar Pré-teste",
            command=lambda: self.import_csv(phase="Pré-teste")
        )
        self.btn_import_pos = ttk.Button(
            self,
            text="Adicionar Pós-teste",
            command=lambda: self.import_csv(phase="Pós-teste"),
            state="disabled"
        )
        self.btn_export = ttk.Button(
            self,
            text="Exportar Resultados",
            command=self.abrir_exportacao,
            state="disabled"
        )
        # self.btn_manual = ttk.Button(
        #     self,
        #     text="Inserir Manualmente"
        # )
        # self.btn_manage = ttk.Button(
        #     self,
        #     text="Gerenciar Dados"
        # )
        # self.btn_mds = ttk.Button(
        #     self,
        #     text="Análise MDS",
        #     command= lambda: MDSSession(self, self.dataset),
        #     state="disabled"
        # )

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------
        self.btn_import_pre.pack(side="left", padx=5)
        self.btn_import_pos.pack(side="left", padx=5)
        self.btn_export.pack(side="left", padx=5)
        # self.btn_manual.pack(side="left", padx=5)
        # self.btn_manage.pack(side="left", padx=5)
        # self.btn_mds.pack(side="left", padx=5)

    # toolbar methods:
    def import_csv(self, phase: str = "Pré-teste") -> None:

        file_path = Path(filedialog.askopenfilename(
            filetypes=[
                ("Todos os arquivos", "*.*"),
                ("Arquivos CSV", "*.csv")
            ]
        ))
        # import canceled
        if not file_path.name:
            return

        try:
            ext = file_path.suffix.lower()
            if ext == ".csv":
                df = load_csv(file_path)
            else:
                messagebox.showerror("Erro", "Tipo de arquivo não suportado")
                return

            # detects file type:
            file_type = detect_file_type(df, ext)

            participants_data, headers = separate_df(df, file_type, ext)

            unk_group = any(p.group == ' - ' for p in participants_data)
            # print(any(p.group == ' - ' for p in participants_data))

            if unk_group:
                def on_confirm(new_group: str):
                    for p in participants_data:
                        if p.group == ' - ':
                            p.group = new_group

                dialog = GroupMappingWindow(self, on_confirm)
                self.wait_window(dialog)


            # Set the phase manually for all participants
            for p in participants_data:
                p.phase = phase

            if phase == "Pré-teste":
                self.dataset.set_new_participants(participants_data)
                self.dataset.set_headers(headers)
                # Habilita o botão do pós-teste
                self.btn_import_pos.state(["!disabled"])
            else:
                # Se for Pós-teste, apenas adiciona ao dataset existente
                self.dataset.add_participants(participants_data)

            # Se não tem alunos, talvez nem faça sentido continuar o plot
            if not self.dataset.has_students:
                messagebox.showerror("Erro Crítico", "Não há dados de alunos para visualizar.")
                return

            # Alerta caso algum grupo esteja vazio
            if not self.dataset.has_professors:
                missing = []
                if not self.dataset.has_professors: missing.append("Professores (Gabarito)")

                msg = f"Aviso: O arquivo não contém dados de:\n\n{', '.join(missing)}.\n\n"
                msg += "Algumas funcionalidades de comparação e exportação estarão desabilitadas."
                messagebox.showwarning("Importação Parcial", msg)

            # ---------------------------------

            if not headers:
                messagebox.showerror("Erro", "Nenhuma informação válida encontrada.")
                return

            # def on_confirm(new_headers: list[str]) -> None:
            #     self.dataset.set_selected_headers(new_headers)
            #
            #     # show first participant
            #     self.visualization_area.show_dataframe(self.dataset, index=0)
            #
            #     self.control_panel.refresh()
            #
            # dialog = ImportDialog(self, headers, on_confirm)
            # self.wait_window(dialog)
            self.dataset.set_selected_headers(headers)

            self.dataset.calc_mean()

            self.visualization_area.create_dataframe()
            self.visualization_area.create_mds()

            self.control_panel.refresh()
            
            if phase == "Pré-teste":
                self.control_panel.phase_var.set("pre")
            else:
                self.control_panel.phase_var.set("pos")
                
            self.control_panel._enable_ctrl() # força a UI a ler o novo valor de phase_var

            self.visualization_area.refresh()

            self.btn_export.state(["!disabled"])


        except Exception as e:
            messagebox.showerror("Erro ao importar CSV", str(e))

    # Na sua classe principal App:
    def abrir_exportacao(self):
        # Passa o self.dataset ou objeto que contém os dados processados
        filtered = getattr(self.control_panel, "filtered_indices", None)
        export_dialog = ExportWindow(self, self.dataset, filtered)
        self.wait_window(export_dialog)