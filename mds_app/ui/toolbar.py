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
        self.dataset_mode = "group"
        self.main_window = None

        self._create_widgets()
        self.configure(height=100)

    # create the toolbar area:
    def _create_widgets(self) -> None:
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # Selector de modo
        self.lbl_mode = ttk.Label(self, text="Modo de Operação:")
        self.mode_var = tk.StringVar(value="Análise de Grupo")
        self.mode_combo = ttk.Combobox(
            self, 
            textvariable=self.mode_var,
            values=["Análise de Grupo", "Análise de Matriz Única"],
            state="readonly",
            width=22
        )
        self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

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
        self.btn_import_single = ttk.Button(
            self,
            text="Importar Matriz",
            command=self.import_single_matrix
        )
        self.btn_export = ttk.Button(
            self,
            text="Exportar Resultados",
            command=self.abrir_exportacao,
            state="disabled"
        )

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------
        self.lbl_mode.pack(side="left", padx=(10, 5))
        self.mode_combo.pack(side="left", padx=5)

        # Empacota os botões do modo grupo inicialmente
        self.btn_import_pre.pack(side="left", padx=5)
        self.btn_import_pos.pack(side="left", padx=5)
        self.btn_export.pack(side="left", padx=5)

    def _on_mode_change(self, event=None) -> None:
        if self.main_window:
            val = self.mode_var.get()
            if val == "Análise de Grupo":
                self.main_window.set_mode("group")
            else:
                self.main_window.set_mode("single")

    def set_mode(self, mode: str) -> None:
        self.btn_import_pre.pack_forget()
        self.btn_import_pos.pack_forget()
        self.btn_import_single.pack_forget()
        self.btn_export.pack_forget()

        if mode == "group":
            self.mode_var.set("Análise de Grupo")
            self.btn_import_pre.pack(side="left", padx=5)
            self.btn_import_pos.pack(side="left", padx=5)
            
            # Atualizar estados de habilitado dos botões
            if self.dataset.participants and self.dataset.has_students:
                self.btn_export.state(["!disabled"])
                has_pos = any(p.dataframe_pos is not None for p in self.dataset.participants["professors"] + self.dataset.participants["students"])
                if has_pos:
                    self.btn_import_pos.state(["!disabled"])
                else:
                    self.btn_import_pos.state(["disabled"])
            else:
                self.btn_import_pos.state(["disabled"])
                self.btn_export.state(["disabled"])
                
            self.btn_export.pack(side="left", padx=5)
        else:
            self.mode_var.set("Análise de Matriz Única")
            self.btn_import_single.pack(side="left", padx=5)
            
            # Habilitar exportação se houver matriz única carregada
            if self.dataset.participants and self.dataset.participants.get("students"):
                self.btn_export.state(["!disabled"])
            else:
                self.btn_export.state(["disabled"])
                
            self.btn_export.pack(side="left", padx=5)

    def import_single_matrix(self) -> None:
        file_path = Path(filedialog.askopenfilename(
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*")
            ]
        ))
        if not file_path.name:
            return

        try:
            ext = file_path.suffix.lower()
            if ext == ".csv":
                df = load_csv(file_path)
            else:
                messagebox.showerror("Erro", "Tipo de arquivo não suportado")
                return

            file_type = detect_file_type(df, ext)
            
            # Se for do tipo forms, processamos os participantes e pedimos para escolher um
            if file_type == "forms":
                participants_data, headers = separate_df(df, file_type, ext)
                if not participants_data:
                    messagebox.showerror("Erro", "Nenhum participante encontrado no arquivo.")
                    return
                
                if len(participants_data) > 1:
                    # Diálogo para escolher qual participante
                    choose_win = tk.Toplevel(self)
                    choose_win.title("Selecionar Participante")
                    choose_win.geometry("350x180")
                    choose_win.transient(self)
                    choose_win.grab_set()
                    
                    choose_win.update_idletasks()
                    x = self.winfo_x() + (self.winfo_width() - choose_win.winfo_width()) // 2
                    y = self.winfo_y() + (self.winfo_height() - choose_win.winfo_height()) // 2
                    choose_win.geometry(f"+{x}+{y}")
                    
                    ttk.Label(choose_win, text="O arquivo contém múltiplos participantes.\nSelecione qual deseja visualizar na Matriz Única:", justify="center").pack(pady=10)
                    
                    p_names = [p.name for p in participants_data]
                    p_var = tk.StringVar()
                    combo = ttk.Combobox(choose_win, textvariable=p_var, values=p_names, state="readonly", width=30)
                    combo.pack(pady=5)
                    combo.current(0)
                    
                    selected_p = [None]
                    
                    def on_select():
                        name = p_var.get()
                        selected_p[0] = next(p for p in participants_data if p.name == name)
                        choose_win.destroy()
                        
                    ttk.Button(choose_win, text="Visualizar", command=on_select).pack(pady=15)
                    self.wait_window(choose_win)
                    
                    if selected_p[0] is None:
                        return
                        
                    p_chosen = selected_p[0]
                else:
                    p_chosen = participants_data[0]
                    
                p_chosen.pid = 0
                participants_data = [p_chosen]
            
            elif file_type != "matrix":
                confirm = messagebox.askyesno(
                    "Tipo de Arquivo Diferente",
                    "Este arquivo não foi detectado automaticamente como uma matriz quadrada simétrica.\n"
                    "Deseja tentar importá-lo de qualquer forma como matriz de dissimilaridade?"
                )
                if not confirm:
                    return
                file_type = "matrix"
                participants_data, headers = separate_df(df, file_type, ext)
            else:
                participants_data, headers = separate_df(df, file_type, ext)

            if not participants_data or not headers:
                messagebox.showerror("Erro", "Nenhuma matriz válida encontrada.")
                return

            # Validação e edição dos termos importados (Conforme A3)
            from mds_app.ui.concept_manager_window import ConceptManagerWindow
            from mds_app.ui.manual_input_window import ManualInputWindow

            def on_confirm_concepts(new_headers: list[str]) -> None:
                mat_confirmed = False

                def on_confirm_matrix(df: pd.DataFrame) -> None:
                    nonlocal df_mat, mat_confirmed
                    df_mat = df
                    mat_confirmed = True
                
                p = participants_data[0]
                df_mat = p.dataframe_pre.copy()
                
                old_set = set(headers)
                new_set = set(new_headers)
                new_concepts = new_set - old_set

                if (new_set != old_set) or (len(new_headers) != len(headers)):
                    # redimensiona a matriz:
                    df_mat = df_mat.reindex(index=new_headers, columns=new_headers)

                    # garante que a diagonal permaneça com valor 0:
                    for h in new_headers:
                        df_mat.at[h, h] = 0.0
                    
                    # se houver mais conceitos, abre a janela de edição da matriz antes de salvar:
                    if (new_set != old_set) or (len(new_headers) > len(headers)):
                        dialog_matrix = ManualInputWindow(self, new_headers, on_confirm_matrix, df_mat, title="Preencher Matriz Única")
                        self.wait_window(dialog_matrix)

                        if not mat_confirmed:
                            return

                    p.dataframe_pre = df_mat
                else:
                    df_mat.columns = new_headers
                    df_mat.index = new_headers
                
                p.mds_result_pre.fit(df_mat)

                self.dataset.set_new_participants([p])
                self.dataset.set_headers(new_headers)
                self.dataset.set_selected_headers(new_headers)
                self.dataset.calc_mean()

                self.visualization_area.create_dataframe()
                self.visualization_area.create_mds()
                self.control_panel.refresh()
                self.visualization_area.refresh()

                dialog.destroy()

            # Abrir diálogo
            dialog = ConceptManagerWindow(self, headers, on_confirm_concepts, title="Validar Conceitos da Matriz")
            self.wait_window(dialog)

        except Exception as e:
            messagebox.showerror("Erro ao importar matriz", str(e))

    # toolbar methods:
    def import_csv(self, phase: str = "Pré-teste") -> None:

        file_path = Path(filedialog.askopenfilename(
            filetypes=[
                ("Arquivos CSV", "*.csv"),
                ("Todos os arquivos", "*.*")
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