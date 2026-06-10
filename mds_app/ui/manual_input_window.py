import tkinter as tk
from tkinter import ttk, messagebox
from tksheet import Sheet
import pandas as pd
import numpy as np

class ManualInputWindow(tk.Toplevel):
    def __init__(self, parent, concepts: list[str], on_confirm, init_df: pd.DataFrame | None = None, title: str = "Preencher Matriz de Dissimilaridade") -> None:
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("600x500")
        self.minsize(500, 400)
        self.transient(parent)
        self.grab_set()

        self.concepts = list(concepts)
        self.on_confirm = on_confirm
        self.df = init_df
        self.confirmed = False
        self.editable_cells = [(r, c) for r in range(len(self.concepts)) for c in range(len(self.concepts)) if r > c]
        self.prev_cell = self.editable_cells[0] if self.editable_cells else (1, 0)

        self._create_widgets()
        
        # Centralizar
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

    def _create_widgets(self) -> None:
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        lbl_info = ttk.Label(
            main_frame,
            text="Digite os valores de dissimilaridade (distâncias) na planilha abaixo.\n"
                 "Preencha apenas o triângulo inferior. A diagonal e o triângulo superior estão travados.",
            font=("Segoe UI", 9)
        )
        lbl_info.pack(fill="x", pady=(0, 10))

        num = len(self.concepts)

        if self.df is None:
            data = []

            for r in range(num):
                row_data = []
                for c in range(num):
                    if r <= c:
                        if r == c:
                            row_data.append(0.0)
                        else:
                            row_data.append("-")
                    else:
                        row_data.append(0.0)
                data.append(row_data)
        else:
            data = self.df.values.tolist()

            for r in range(num):
                for c in range(num):
                    if r < c:
                        data[r][c] = "-"

        self.sheet = Sheet(
            main_frame,
            data=data,
            headers=self.concepts,
            row_index=self.concepts,
            show_x_scrollbar=True,
            show_y_scrollbar=True,
            show_top_left=True
        )
        self.sheet.enable_bindings(
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
            "edit_cell"
        )
        self.sheet.extra_bindings([("end_edit_cell", self.on_cell_edited), ("select_cell", self.on_select_cell)])
        self.sheet.pack(fill="both", expand=True, pady=5)

        # Ajustar tamanhos
        size = 50
        self.sheet.set_all_column_widths(size)
        self.sheet.set_all_row_heights(size)
        
        # Colorir e tornar o triângulo superior e a diagonal como somente leitura
        readonly_list = []
        for r in range(num):
            for c in range(num):
                if r <= c:
                    readonly_list.append((r, c))
                    bg_color = "#e0e0e0" if r == c else "#f2f2f2"
                    fg_color = "#808080"
                    self.sheet.highlight_cells(row=r, column=c, bg=bg_color, fg=fg_color)
        
        try:
            self.sheet.readonly_cells(cells=readonly_list)
        except Exception as e:
            # Fallback seguro caso a API do tksheet seja diferente
            print(f"tksheet readonly_cells fallback: {e}")

        # Botões
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", side="bottom", pady=(10, 0))

        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        self.btn_cancel.pack(side="right", padx=5)

        self.btn_ok = ttk.Button(btn_frame, text="Confirmar", command=self._confirm)
        self.btn_ok.pack(side="right", padx=5)

    def on_cell_edited(self, event) -> None:
        try:
            row, col, value_before, value_after, *rest = event
        except Exception:
            return

        # Impedir edições na diagonal ou triângulo superior
        if row <= col:
            if row == col:
                self.sheet.set_cell_data(row, col, 0.0)
            else:
                self.sheet.set_cell_data(row, col, "-")
            return

        try:
            if value_after == "-" or value_after == "" or value_after is None:
                val_num = np.nan
            else:
                val_num = float(value_after)
        except ValueError:
            self.sheet.set_cell_data(row, col, value_before)
            return

    def on_select_cell(self, event) -> None:
        try:
            row, col = event[0], event[1]
        except Exception:
            return

        # Se for uma célula editável, apenas atualiza prev_cell e retorna
        if row > col:
            self.prev_cell = (row, col)
            return

        # Célula bloqueada. Precisamos pular para a próxima editável baseando-se no movimento.
        if not self.editable_cells:
            return

        r_prev, c_prev = self.prev_cell
        
        try:
            i_prev = self.editable_cells.index((r_prev, c_prev))
        except ValueError:
            i_prev = 0

        num = len(self.concepts)
        
        # Determinar a direção do movimento
        if row > r_prev and col == c_prev:
            # Movimento para Baixo (Enter/Down) -> Procurar na mesma coluna
            found = False
            for r in range(row, num):
                if r > col:
                    self.sheet.select_cell(r, col)
                    self.sheet.see(r, col, keep_selection=True)
                    self.prev_cell = (r, col)
                    found = True
                    break
            if not found:
                for r in range(0, row):
                    if r > col:
                        self.sheet.select_cell(r, col)
                        self.sheet.see(r, col, keep_selection=True)
                        self.prev_cell = (r, col)
                        break
                        
        elif row < r_prev and col == c_prev:
            # Movimento para Cima (Up) -> Procurar na mesma coluna subindo
            found = False
            for r in range(row, -1, -1):
                if r > col:
                    self.sheet.select_cell(r, col)
                    self.sheet.see(r, col, keep_selection=True)
                    self.prev_cell = (r, col)
                    found = True
                    break
            if not found:
                for r in range(num - 1, row, -1):
                    if r > col:
                        self.sheet.select_cell(r, col)
                        self.sheet.see(r, col, keep_selection=True)
                        self.prev_cell = (r, col)
                        break
                        
        elif col < c_prev or (row < r_prev and c_prev == 0):
            # Movimento para Trás (Shift-Tab / Left) -> Ir para o editável anterior na lista
            next_idx = (i_prev - 1) % len(self.editable_cells)
            r_next, c_next = self.editable_cells[next_idx]
            self.sheet.select_cell(r_next, c_next)
            self.sheet.see(r_next, c_next, keep_selection=True)
            self.prev_cell = (r_next, c_next)
            
        else:
            # Movimento para Frente (Tab / Right) -> Ir para o próximo editável na lista
            next_idx = (i_prev + 1) % len(self.editable_cells)
            r_next, c_next = self.editable_cells[next_idx]
            self.sheet.select_cell(r_next, c_next)
            self.sheet.see(r_next, c_next, keep_selection=True)
            self.prev_cell = (r_next, c_next)

    def _confirm(self) -> None:
        sheet_data = self.sheet.get_sheet_data()
        
        # Construir matriz simétrica de floats no DataFrame
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
        
        if df.isna().any().any():
            confirm = messagebox.askyesno(
                "Aviso",
                "A matriz possui campos em branco. Deseja confirmar e prosseguir?",
                parent=self
            )
            if not confirm:
                return

        self.confirmed = True
        self.on_confirm(df)
        self.destroy()
