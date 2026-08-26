import tkinter as tk
from tkinter import ttk, messagebox
from tksheet import Sheet
import pandas as pd
import numpy as np
from mds_app.data.dataset import Dataset
from mds_app.data.participant import Participant

class ParticipantManagerWindow(tk.Toplevel):
    def __init__(self, parent, dataset: Dataset, participant: Participant | None = None, on_confirm=None, title: str = "") -> None:
        super().__init__(parent)
        self.parent = parent
        self.dataset = dataset
        self.participant = participant
        self.on_confirm = on_confirm
        self.confirmed = False

        self.concepts = list(dataset.headers) if dataset.headers else []
        self.is_edit_mode = participant is not None

        # Configuração do título padrão
        if not title:
            self.title("Editar Participante" if self.is_edit_mode else "Novo Participante")
        else:
            self.title(title)

        self.geometry("650x550")
        self.minsize(550, 450)
        self.transient(parent)
        self.grab_set()

        # Variáveis cadastrais
        self.name_var = tk.StringVar(value=participant.name if self.is_edit_mode else "")
        self.group_var = tk.StringVar(value=participant.group if self.is_edit_mode else "Aluno")
        self.level_var = tk.StringVar(value=participant.familiarity_level if self.is_edit_mode else "Médio")

        # Configurações de navegação do tksheet
        self.editable_cells = [(r, c) for r in range(len(self.concepts)) for c in range(len(self.concepts)) if r > c]
        self.prev_cell_pre = self.editable_cells[0] if self.editable_cells else (1, 0)
        self.prev_cell_pos = self.editable_cells[0] if self.editable_cells else (1, 0)

        self.pre_sheet: Sheet | None = None
        self.pos_sheet: Sheet | None = None
        self.pos_container: ttk.Frame | None = None
        self.has_pos_data = False

        if self.is_edit_mode and participant.dataframe_pos is not None:
            self.has_pos_data = True

        self._create_widgets()

        # Centralizar na tela em relação ao pai
        self.update_idletasks()
        root_window = self.parent.winfo_toplevel()
        root_window.update_idletasks()

        root_x = root_window.winfo_rootx()
        root_y = root_window.winfo_rooty()
        root_width = root_window.winfo_width()
        root_height = root_window.winfo_height()

        w = self.winfo_width()
        h = self.winfo_height()

        x = root_x + (root_width - w) // 2
        y = root_y + (root_height - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.focus_set()

    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Notebook com as abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True, pady=(0, 10))

        # ----------------------------------------------------
        # ABA 1: Informações Pessoais
        # ----------------------------------------------------
        info_tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(info_tab, text="Informações")

        lbl_name = ttk.Label(info_tab, text="Nome / Código de Identificação:", font=("Segoe UI", 9, "bold"))
        lbl_name.pack(anchor="w", pady=(0, 5))
        self.ent_name = ttk.Entry(info_tab, textvariable=self.name_var)
        self.ent_name.pack(fill="x", pady=(0, 15))

        lbl_group = ttk.Label(info_tab, text="Grupo:", font=("Segoe UI", 9, "bold"))
        lbl_group.pack(anchor="w", pady=(0, 5))
        group_frame = ttk.Frame(info_tab)
        group_frame.pack(fill="x", pady=(0, 15))
        r_aluno = ttk.Radiobutton(group_frame, text="Aluno", value="Aluno", variable=self.group_var)
        r_aluno.pack(side="left", padx=(0, 20))
        r_prof = ttk.Radiobutton(group_frame, text="Professor", value="Professor", variable=self.group_var)
        r_prof.pack(side="left")

        lbl_level = ttk.Label(info_tab, text="Nível de Familiaridade:", font=("Segoe UI", 9, "bold"))
        lbl_level.pack(anchor="w", pady=(0, 5))
        level_frame = ttk.Frame(info_tab)
        level_frame.pack(fill="x", pady=(0, 20))
        levels = ["Nenhum", "Baixo", "Médio", "Alto", "Avançado"]
        for lvl in levels:
            r_lvl = ttk.Radiobutton(level_frame, text=lvl, value=lvl, variable=self.level_var)
            r_lvl.pack(side="left", expand=True, anchor="w")

        # ----------------------------------------------------
        # ABA 2: Pré-teste
        # ----------------------------------------------------
        pre_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(pre_tab, text="Matriz Pré-teste")
        
        lbl_pre_info = ttk.Label(
            pre_tab,
            text="Preencha as dissimilaridades do Pré-teste (apenas triângulo inferior).",
            font=("Segoe UI", 9, "italic")
        )
        lbl_pre_info.pack(anchor="w", pady=(0, 5))

        # Obter df_pre
        df_pre = self.participant.dataframe_pre if self.is_edit_mode else None
        self.pre_sheet = self._create_matrix_sheet(pre_tab, df_pre, phase="pre")
        self.pre_sheet.pack(fill="both", expand=True)

        # ----------------------------------------------------
        # ABA 3: Pós-teste
        # ----------------------------------------------------
        self.pos_tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.pos_tab, text="Matriz Pós-teste")
        self._build_pos_tab()

        # ----------------------------------------------------
        # BOTÕES DE AÇÃO (CONFIRMAR/CANCELAR)
        # ----------------------------------------------------
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", side="bottom")

        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar", command=self._cancel)
        self.btn_cancel.pack(side="right", padx=5)

        self.btn_ok = ttk.Button(btn_frame, text="Salvar", command=self._confirm)
        self.btn_ok.pack(side="right", padx=5)

        # Binds de atalho
        self.bind("<Escape>", lambda e: self._cancel())

    def _build_pos_tab(self) -> None:
        # Limpar widgets anteriores da aba de pós-teste
        for child in self.pos_tab.winfo_children():
            child.destroy()

        if self.has_pos_data:
            lbl_pos_info = ttk.Label(
                self.pos_tab,
                text="Preencha as dissimilaridades do Pós-teste (apenas triângulo inferior).",
                font=("Segoe UI", 9, "italic")
            )
            lbl_pos_info.pack(anchor="w", pady=(0, 5))

            df_pos = self.participant.dataframe_pos if (self.is_edit_mode and self.participant.dataframe_pos is not None) else None
            self.pos_sheet = self._create_matrix_sheet(self.pos_tab, df_pos, phase="pos")
            self.pos_sheet.pack(fill="both", expand=True)

            # Botão para remover os dados de pós-teste
            btn_remove_pos = ttk.Button(
                self.pos_tab,
                text="Excluir Dados do Pós-teste",
                style="danger.TButton",
                command=self._remove_pos_data
            )
            btn_remove_pos.pack(anchor="e", pady=(5, 0))
        else:
            self.pos_sheet = None
            container = ttk.Frame(self.pos_tab)
            container.pack(fill="both", expand=True)
            
            ttk.Label(
                container,
                text="Nenhum dado de Pós-teste cadastrado para este participante.",
                foreground="gray",
                font=("Segoe UI", 10),
                justify="center"
            ).pack(pady=(50, 10))

            btn_enable = ttk.Button(
                container,
                text="Habilitar Matriz de Pós-teste",
                command=self._enable_pos_data
            )
            btn_enable.pack(pady=10)

    def _enable_pos_data(self) -> None:
        self.has_pos_data = True
        self._build_pos_tab()

    def _remove_pos_data(self) -> None:
        confirm = messagebox.askyesno(
            "Confirmar Remoção",
            "Deseja realmente remover os dados do pós-teste deste participante?",
            parent=self
        )
        if confirm:
            self.has_pos_data = False
            self._build_pos_tab()

    def _create_matrix_sheet(self, parent_frame: ttk.Frame, df: pd.DataFrame | None, phase: str) -> Sheet:
        num = len(self.concepts)
        data = []

        if df is None:
            for r in range(num):
                row_data = []
                for c in range(num):
                    if r <= c:
                        row_data.append(0.0 if r == c else "-")
                    else:
                        row_data.append(0.0)
                data.append(row_data)
        else:
            data = df.values.tolist()
            for r in range(num):
                for c in range(num):
                    if r < c:
                        data[r][c] = "-"

        sheet = Sheet(
            parent_frame,
            data=data,
            headers=self.concepts,
            row_index=self.concepts,
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            show_top_left=True
        )
        sheet.enable_bindings(
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
            "edit_cell",
            "copy"
        )
        
        # Binds específicos de validação e pulo de célula
        sheet.extra_bindings([
            ("end_edit_cell", lambda event: self._on_cell_edited(event, sheet)),
            ("select", lambda event: self._on_select_cell(event, sheet, phase))
        ])

        # Ajustar tamanhos padrão
        size = 45
        sheet.set_all_column_widths(size)
        sheet.set_all_row_heights(size)

        # Destacar e travar diagonal e triângulo superior
        readonly_list = []
        diagonal_cells = []
        upper_triangle_cells = []
        for r in range(num):
            for c in range(num):
                if r <= c:
                    readonly_list.append((r, c))
                    if r == c:
                        diagonal_cells.append((r, c))
                    else:
                        upper_triangle_cells.append((r, c))
        
        if diagonal_cells:
            sheet.highlight_cells(cells=diagonal_cells, bg="#e0e0e0", fg="#808080", redraw=False)
        if upper_triangle_cells:
            sheet.highlight_cells(cells=upper_triangle_cells, bg="#f2f2f2", fg="#808080", redraw=False)
        
        try:
            sheet.readonly_cells(cells=readonly_list)
        except Exception as e:
            print(f"tksheet readonly_cells fallback: {e}")

        return sheet

    def _on_cell_edited(self, event, sheet: Sheet) -> None:
        try:
            ((row, col), value_before), = event.cells.table.items()
            value_after = event.data.get((row, col))
        except Exception:
            return

        if row <= col:
            if row == col:
                sheet.set_cell_data(row, col, 0.0)
            else:
                sheet.set_cell_data(row, col, "-")
            return

        try:
            if value_after == "-" or value_after == "" or value_after is None or str(value_after).strip() == "":
                val_num = np.nan
            else:
                val_num = float(value_after)
                if val_num < 0:
                    raise ValueError("A distância não pode ser negativa.")
        except ValueError as e:
            sheet.set_cell_data(row, col, value_before)
            messagebox.showerror("Erro de Formato", f"Por favor insira um número válido não-negativo.\nErro: {e}", parent=self)
            return

    def _on_select_cell(self, event, sheet: Sheet, phase: str) -> None:
        try:
            _selected = event.selected
            row, col = _selected.row, _selected.column
        except Exception:
            return

        if row > col:
            if phase == "pre":
                self.prev_cell_pre = (row, col)
            else:
                self.prev_cell_pos = (row, col)
            return

        if not self.editable_cells:
            return

        r_prev, c_prev = self.prev_cell_pre if phase == "pre" else self.prev_cell_pos
        
        try:
            i_prev = self.editable_cells.index((r_prev, c_prev))
        except ValueError:
            i_prev = 0

        num = len(self.concepts)
        
        # Pular células travadas conforme direção
        if row == 0 and col > c_prev:
            found = False
            for r in range(row, num):
                if r > col:
                    sheet.select_cell(r, col)
                    sheet.see(r, col)
                    if phase == "pre": self.prev_cell_pre = (r, col)
                    else: self.prev_cell_pos = (r, col)
                    found = True
                    break
            if not found:
                col = 0
                for r in range(0, num):
                    if r > col:
                        sheet.select_cell(r, col)
                        sheet.see(r, col)
                        if phase == "pre": self.prev_cell_pre = (r, col)
                        else: self.prev_cell_pos = (r, col)
                        break
                        
        elif row < r_prev and col == c_prev:
            found = False
            for r in range(row, -1, -1):
                if r > col:
                    sheet.select_cell(r, col)
                    sheet.see(r, col)
                    if phase == "pre": self.prev_cell_pre = (r, col)
                    else: self.prev_cell_pos = (r, col)
                    found = True
                    break
            if not found:
                col = (col-1) if col > 0 else num-2
                for r in range(num - 1, 0, -1):
                    if r > col:
                        sheet.select_cell(r, col)
                        sheet.see(r, col)
                        if phase == "pre": self.prev_cell_pre = (r, col)
                        else: self.prev_cell_pos = (r, col)
                        break
                        
        elif col < c_prev or (row < r_prev and c_prev == 0):
            next_idx = (i_prev - 1) % len(self.editable_cells)
            r_next, c_next = self.editable_cells[next_idx]
            sheet.select_cell(r_next, c_next)
            sheet.see(r_next, c_next)
            if phase == "pre": self.prev_cell_pre = (r_next, c_next)
            else: self.prev_cell_pos = (r_next, c_next)
            
        else:
            next_idx = (i_prev + 1) % len(self.editable_cells)
            r_next, c_next = self.editable_cells[next_idx]
            sheet.select_cell(r_next, c_next)
            sheet.see(r_next, c_next)
            if phase == "pre": self.prev_cell_pre = (r_next, c_next)
            else: self.prev_cell_pos = (r_next, c_next)

    def _parse_sheet_matrix(self, sheet: Sheet) -> pd.DataFrame:
        sheet_data = sheet.get_sheet_data()
        num = len(self.concepts)
        df = pd.DataFrame(0.0, index=self.concepts, columns=self.concepts, dtype=float)
        
        for r in range(num):
            for c in range(num):
                if r == c:
                    df.iloc[r, c] = 0.0
                elif r > c:
                    val = sheet_data[r][c]
                    try:
                        if val == "-" or val == "" or val is None or str(val).strip() == "":
                            val_num = np.nan
                        else:
                            val_num = float(val)
                    except ValueError:
                        val_num = np.nan
                    df.iloc[r, c] = val_num
                    df.iloc[c, r] = val_num
        return df

    def _confirm(self) -> None:
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Erro de Validação", "O nome do participante é obrigatório.", parent=self)
            return

        # Verificar duplicatas
        existing_names = []
        if self.dataset.participants:
            for gk in ["students", "professors"]:
                for p in self.dataset.participants[gk]:
                    # Ignorar o próprio participante sendo editado
                    if self.is_edit_mode and p.name.lower().strip() == self.participant.name.lower().strip():
                        continue
                    existing_names.append(p.name.lower().strip())

        if name.lower().strip() in existing_names:
            messagebox.showerror("Erro de Validação", f"Já existe um participante com o nome '{name}'.", parent=self)
            return

        # Converter planilhas em dataframes
        df_pre = self._parse_sheet_matrix(self.pre_sheet)
        
        df_pos = None
        if self.has_pos_data and self.pos_sheet:

            df_pos = self._parse_sheet_matrix(self.pos_sheet)

        # Alertas sobre nulos
        has_nans = df_pre.isna().any().any() or (df_pos is not None and df_pos.isna().any().any())
        if has_nans:
            confirm = messagebox.askyesno(
                "Dados Pendentes",
                "Algumas células das planilhas estão em branco. Elas serão salvas como nulas (NaN).\nDeseja continuar?",
                parent=self
            )
            if not confirm:
                return

        self.confirmed = True

        # Estrutura do resultado
        self.result = {
            "name": name,
            "group": self.group_var.get(),
            "familiarity_level": self.level_var.get(),
            "df_pre": df_pre,
            "df_pos": df_pos
        }

        if self.on_confirm:
            self.on_confirm(self.result)

        self.grab_release()
        self.destroy()

    def _cancel(self) -> None:
        self.confirmed = False
        self.grab_release()
        self.destroy()
