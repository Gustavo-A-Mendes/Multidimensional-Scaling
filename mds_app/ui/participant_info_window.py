import tkinter as tk
from tkinter import ttk, messagebox
from mds_app.data.dataset import Dataset

class ParticipantInfoWindow(tk.Toplevel):
    def __init__(self, parent, dataset: Dataset, title: str = "Informações do Participante") -> None:
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("450x440")
        self.minsize(400, 380)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.dataset = dataset
        self.students = self.dataset.participants.get("students", []) if self.dataset.participants else []
        self.professors = self.dataset.participants.get("professors", []) if self.dataset.participants else []
        self.all_participants = self.students + self.professors
        self.existing_names = [p.name.lower().strip() for p in self.all_participants]

        self.confirmed = False
        self.result = {}

        self._create_widgets()
        self._on_phase_change()
        
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
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Fase da Análise
        lbl_phase = ttk.Label(main_frame, text="Fase da Análise:", font=("Segoe UI", 9, "bold"))
        lbl_phase.pack(anchor="w", pady=(0, 5))
        
        self.phase_var = tk.StringVar(value="pre")
        phase_frame = ttk.Frame(main_frame)
        phase_frame.pack(fill="x", pady=(0, 15))
        
        r_pre = ttk.Radiobutton(phase_frame, text="Pré-teste", value="pre", variable=self.phase_var, command=self._on_phase_change)
        r_pre.pack(side="left", padx=(0, 20))
        
        r_pos = ttk.Radiobutton(phase_frame, text="Pós-teste", value="pos", variable=self.phase_var, command=self._on_phase_change)
        r_pos.pack(side="left")
        
        # Se não há participantes no dataset, desabilita a opção de pós-teste
        if not self.all_participants:
            r_pos.configure(state="disabled")

        # Campo Nome/Código (Combobox)
        lbl_name = ttk.Label(main_frame, text="Nome / Código de Identificação:", font=("Segoe UI", 9, "bold"))
        lbl_name.pack(anchor="w", pady=(0, 5))
        
        self.cmb_name = ttk.Combobox(main_frame, width=40)
        self.cmb_name.pack(fill="x", pady=(0, 15))
        self.cmb_name.bind("<<ComboboxSelected>>", self._on_name_selected)

        # Grupo
        lbl_group = ttk.Label(main_frame, text="Grupo:", font=("Segoe UI", 9, "bold"))
        lbl_group.pack(anchor="w", pady=(0, 5))
        
        self.group_var = tk.StringVar(value="Aluno")
        self.group_frame = ttk.Frame(main_frame)
        self.group_frame.pack(fill="x", pady=(0, 15))
        
        self.r_aluno = ttk.Radiobutton(self.group_frame, text="Aluno", value="Aluno", variable=self.group_var)
        self.r_aluno.pack(side="left", padx=(0, 20))
        
        self.r_prof = ttk.Radiobutton(self.group_frame, text="Professor", value="Professor", variable=self.group_var)
        self.r_prof.pack(side="left")

        # Nível de Familiaridade
        lbl_level = ttk.Label(main_frame, text="Nível de Familiaridade:", font=("Segoe UI", 9, "bold"))
        lbl_level.pack(anchor="w", pady=(0, 5))
        
        self.level_var = tk.StringVar(value="Médio")
        self.level_frame = ttk.Frame(main_frame)
        self.level_frame.pack(fill="x", pady=(0, 20))
        
        levels = ["Nenhum", "Baixo", "Médio", "Alto", "Avançado"]
        self.level_radios = []
        for lvl in levels:
            r_lvl = ttk.Radiobutton(self.level_frame, text=lvl, value=lvl, variable=self.level_var)
            r_lvl.pack(side="left", expand=True, anchor="w")
            self.level_radios.append(r_lvl)

        # Divisor
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.pack(fill="x", pady=(0, 15))

        # Botões de confirmação/cancelamento
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", side="bottom")

        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar", command=self._cancel)
        self.btn_cancel.pack(side="right", padx=5)

        self.btn_ok = ttk.Button(btn_frame, text="Confirmar", command=self._confirm)
        self.btn_ok.pack(side="right", padx=5)

        # Binds de atalho
        self.bind("<Return>", lambda e: self._confirm())
        self.bind("<Escape>", lambda e: self._cancel())

    def _on_phase_change(self) -> None:
        phase = self.phase_var.get()
        if phase == "pre":
            self.cmb_name.configure(state="normal")
            self.cmb_name.set("")
            self.cmb_name["values"] = []
            
            # Reabilitar campos de grupo e nível
            self._set_widgets_state(self.group_frame, "normal")
            self._set_widgets_state(self.level_frame, "normal")
        else: # pos
            # Apenas exibe participantes cadastrados
            names = [p.name for p in self.all_participants]
            self.cmb_name["values"] = names
            self.cmb_name.configure(state="readonly")
            if names:
                self.cmb_name.set(names[0])
                self._on_name_selected()
            else:
                self.cmb_name.set("")

            # Desabilitar campos de grupo e nível
            self._set_widgets_state(self.group_frame, "disabled")
            self._set_widgets_state(self.level_frame, "disabled")

    def _on_name_selected(self, event=None) -> None:
        name = self.cmb_name.get()
        p = next((x for x in self.all_participants if x.name == name), None)
        if p:
            self.group_var.set(p.group)
            self.level_var.set(p.familiarity_level)

    def _set_widgets_state(self, container: ttk.Frame, state: str) -> None:
        for child in container.winfo_children():
            try:
                child.configure(state=state)
            except Exception:
                pass

    def _confirm(self) -> None:
        name = self.cmb_name.get().strip()
        if not name:
            messagebox.showerror("Erro de Validação", "O campo Nome / Código de Identificação é obrigatório.", parent=self)
            return

        phase = self.phase_var.get()
        
        if phase == "pre":
            if name.lower() in self.existing_names:
                messagebox.showerror("Erro de Validação", f"Já existe um participante cadastrado com o nome '{name}'.", parent=self)
                return
        else: # pos
            p_names = [p.name.lower().strip() for p in self.all_participants]
            if name.lower().strip() not in p_names:
                messagebox.showerror("Erro de Validação", f"O participante '{name}' não foi encontrado no dataset.", parent=self)
                return

        self.confirmed = True
        self.result = {
            "name": name,
            "group": self.group_var.get(),
            "familiarity_level": self.level_var.get(),
            "phase": phase
        }
        self.grab_release()
        self.destroy()

    def _cancel(self) -> None:
        self.confirmed = False
        self.grab_release()
        self.destroy()
