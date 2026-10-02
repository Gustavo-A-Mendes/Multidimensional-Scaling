from pathlib import Path

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from mds_app.ui.group_mapping_window import GroupMappingWindow
from mds_app.utils.csv_loader import *
from mds_app.utils.validators import *
from mds_app.ui.export_window import ExportWindow

from mds_app.data.dataset import Dataset
from mds_app.ui.control_panel import ControlPanel
from mds_app.ui.visualization_area import VisualizationArea

class ToolBar(ttk.Frame):
    def __init__(self, parent, dataset: Dataset, control_panel: ControlPanel, visualization_area: VisualizationArea, mediator=None) -> None:
        super().__init__(parent)
        self.parent = parent
        self.dataset = dataset
        self.control_panel = control_panel
        self.visualization_area = visualization_area
        self.mediator = mediator if mediator else getattr(control_panel, "mediator", None)
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
        self.btn_import_data = ttk.Button(
            self,
            text="Importar Dados",
            command=self.show_import_dialog
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
        self.btn_clear = ttk.Button(
            self,
            text="Limpar Dataset",
            command=self.limpar_dados
        )

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------
        self.lbl_mode.pack(side="left", padx=(10, 5))
        self.mode_combo.pack(side="left", padx=5)

        # Empacota os botões do modo grupo inicialmente
        self.btn_import_data.pack(side="left", padx=5)
        self.btn_export.pack(side="left", padx=5)
        self.btn_clear.pack(side="left", padx=5)

    def _on_mode_change(self, event=None) -> None:
        if self.main_window:
            val = self.mode_var.get()
            if val == "Análise de Grupo":
                self.main_window.set_mode("group")
            else:
                self.main_window.set_mode("single")

    def set_mode(self, mode: str) -> None:
        self.btn_import_data.pack_forget()
        self.btn_import_single.pack_forget()
        self.btn_export.pack_forget()
        self.btn_clear.pack_forget()

        if mode == "group":
            self.mode_var.set("Análise de Grupo")
            self.btn_import_data.pack(side="left", padx=5)
            
            # Atualizar estados de habilitado dos botões
            if self.dataset.participants and self.dataset.has_students:
                self.btn_export.state(["!disabled"])
            else:
                self.btn_export.state(["disabled"])
                
            self.btn_export.pack(side="left", padx=5)
            self.btn_clear.pack(side="left", padx=5)
        else:
            self.mode_var.set("Análise de Matriz Única")
            self.btn_import_single.pack(side="left", padx=5)

    def _center_window(self, window: tk.Toplevel, width: int = None, height: int = None) -> None:
        """Centraliza uma janela Toplevel em relação à janela principal."""
        window.update_idletasks()
        root_window = self.winfo_toplevel()
        root_window.update_idletasks()
        w = width or window.winfo_width()
        h = height or window.winfo_height()
        x = root_window.winfo_rootx() + (root_window.winfo_width() - w) // 2
        y = root_window.winfo_rooty() + (root_window.winfo_height() - h) // 2
        window.geometry(f"{w}x{h}+{x}+{y}")

    def import_single_matrix(self) -> None:
        if self.dataset.participants:
            confirm = messagebox.askyesno(
                "Aviso de Sobrescrita",
                "Esta ação irá limpar todos os dados atuais do sistema para importar a nova matriz.\nDeseja continuar?",
                parent=self
            )
            if not confirm:
                return

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
                    
                    choose_win.withdraw()
                    choose_win.title("Selecionar Participante")
                    choose_win.geometry("350x180")
                    choose_win.transient(self)
                    choose_win.grab_set()
                    
                    self._center_window(choose_win, 350, 180)
                    choose_win.deiconify()
                    
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

            def on_confirm_concepts(concept_mapping: list[tuple[str,str]]) -> None:
                mat_confirmed = False

                def on_confirm_matrix(df: pd.DataFrame) -> None:
                    nonlocal df_mat, mat_confirmed
                    df_mat = df
                    mat_confirmed = True
                
                p = participants_data[0]
                df_mat = p.dataframe_pre.copy()
                
                # identifica os conceitos novos e os renomeados:
                renamed_dic = {}
                final_headers = []
                has_new_concept = False

                for (nome_atual, nome_original) in concept_mapping:
                    final_headers.append(nome_atual)

                    if nome_original is None:   # há conceito novo
                        has_new_concept = True
                    
                    elif nome_atual != nome_original:
                        renamed_dic[nome_original] = nome_atual
                
                # renomea os nomes alterados:
                if renamed_dic:
                    df_mat = df_mat.rename(index=renamed_dic, columns=renamed_dic)

                # redimensiona a matriz:
                df_mat = df_mat.reindex(index=final_headers, columns=final_headers, fill_value=0.0)

                # garante a diagonal 0:
                for h in final_headers:
                    df_mat.at[h, h] = 0.0
                
                # Se houver mais conceitos, abre a janela de edição da matriz antes de salvar:
                dialog_matrix = ManualInputWindow(self, final_headers, on_confirm_matrix, df_mat, title="Preencher Matriz Única")
                self.wait_window(dialog_matrix)

                if not mat_confirmed:
                    return

                p.dataframe_pre = df_mat
                p.mds_result_pre.fit(df_mat)

                self.dataset.set_new_participants([p])
                self.dataset.set_headers(final_headers)
                self.dataset.set_selected_headers(final_headers)
                if hasattr(self, "mediator") and self.mediator:
                    self.mediator.notify_data_changed()
                else:
                    self.dataset.calc_mean()
                    self.visualization_area.create_dataframe()
                    self.visualization_area.create_mds()
                    self.control_panel.refresh()
                    self.visualization_area.refresh()
                if self.main_window:
                    self.main_window.root.update()
                    self.main_window.main_paned.sash_place(0, 300, 0)

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
            else:
                # Validar cabeçalhos compatíveis entre o Pré-teste e o Pós-teste
                if self.dataset.headers:
                    from mds_app.utils.validators import compare_headers
                    diff = compare_headers(self.dataset.headers, headers)
                    if diff["missing"] or diff["extra"]:
                        msg = "Erro de Incompatibilidade:\n\n"
                        msg += "Os conceitos contidos no arquivo de Pós-teste não coincidem com o Pré-teste já importado.\n\n"
                        if diff["missing"]:
                            msg += f"Conceitos ausentes no Pós-teste: {', '.join(diff['missing'])}\n"
                        if diff["extra"]:
                            msg += f"Conceitos extras no Pós-teste: {', '.join(diff['extra'])}\n"
                        messagebox.showerror("Erro de Importação", msg)
                        return

                # Se for Pós-teste, apenas adiciona ao dataset existente
                self.dataset.add_participants(participants_data, merge_post=True)

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

            self.dataset.set_selected_headers(headers)

            phase_code = "pre" if phase == "Pré-teste" else "pos"
            if hasattr(self, "mediator") and self.mediator:
                self.mediator.phase_var.set(phase_code)
                self.mediator.notify_data_changed()
            else:
                self.dataset.calc_mean()
                self.visualization_area.create_dataframe()
                self.visualization_area.create_mds()
                self.control_panel.refresh()
                self.control_panel.phase_var.set(phase_code)
                self.visualization_area.refresh()

            # Forçar o sash_place após a renderização do gráfico
            if self.main_window:
                self.main_window.root.update()
                self.main_window.main_paned.sash_place(0, 300, 0)

            self.btn_export.state(["!disabled"])

            if phase == "Pré-teste":
                confirm_pos = messagebox.askyesno(
                    "Importação Concluída",
                    "Pré-teste importado com sucesso!\nDeseja importar os dados de Pós-teste agora?",
                    parent=self
                )
                if confirm_pos:
                    self.import_csv(phase="Pós-teste")

        except Exception as e:
            messagebox.showerror("Erro ao importar CSV", str(e))

    def show_import_dialog(self) -> None:
        dialog = tk.Toplevel(self)
        dialog.title("Importar Dados")
        dialog.geometry("380x150")
        dialog.transient(self)
        dialog.grab_set()

        self._center_window(dialog, 380, 150)

        ttk.Label(
            dialog,
            text="Selecione o tipo de dado que deseja importar:",
            font=("Arial", 10, "bold")
        ).pack(pady=(15, 10))

        def on_pre():
            dialog.destroy()
            if self.dataset.participants:
                confirm = messagebox.askyesno(
                    "Aviso de Sobrescrita",
                    "A importação de um novo Pré-teste irá apagar todos os dados atuais do sistema.\nDeseja prosseguir?",
                    parent=self
                )
                if not confirm:
                    return
            self.import_csv(phase="Pré-teste")

        def on_pos():
            dialog.destroy()
            if not self.dataset.participants or not self.dataset.has_students:
                messagebox.showerror(
                    "Erro de Importação",
                    "A importação de Pós-teste requer dados de Pré-teste já carregados.\nImporte o Pré-teste primeiro.",
                    parent=self
                )
                return
            
            # Verificar se já existe pós-teste
            has_pos = any(
                p.dataframe_pos is not None 
                for p in self.dataset.participants.get("students", []) + self.dataset.participants.get("professors", [])
            )
            if has_pos:
                confirm = messagebox.askyesno(
                    "Aviso de Sobrescrita",
                    "Já existem dados de Pós-teste no sistema. Esta ação irá sobrescrever todos os dados de pós-teste atuais.\nDeseja prosseguir?",
                    parent=self
                )
                if not confirm:
                    return
            self.import_csv(phase="Pós-teste")

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Pré-teste", command=on_pre, width=15).pack(side="left", padx=(35, 10))
        ttk.Button(btn_frame, text="Pós-teste", command=on_pos, width=15).pack(side="left", padx=(10, 35))

    # Na sua classe principal App:
    def abrir_exportacao(self):
        # Passa o self.dataset ou objeto que contém os dados processados
        if hasattr(self, "mediator") and self.mediator:
            filtered = self.mediator.get_ranked_indices()
        else:
            filtered = getattr(self.control_panel, "filtered_indices", None)
        export_dialog = ExportWindow(self, self.dataset, filtered)
        self.wait_window(export_dialog)

    def limpar_dados(self) -> None:
        if not self.dataset.participants:
            messagebox.showinfo("Aviso", "O dataset já está vazio.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirmar Limpeza",
            "Tem certeza que deseja limpar todo o dataset? Esta ação não pode ser desfeita e removerá todos os participantes.",
            parent=self
        )
        if confirm:
            if self.main_window:
                self.main_window.clear_dataset()