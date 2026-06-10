import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ConceptManagerWindow(tk.Toplevel):
    def __init__(self, parent, concepts: list[str], on_confirm, title: str = "Gerenciar Conceitos") -> None:
        super().__init__(parent)
        self.parent = parent
        self.title(title)
        self.geometry("400x450")
        # self.minsize(350, 400)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.concepts = list(concepts)
        self.on_confirm = on_confirm
        self.confirmed = False

        self._create_widgets()
        self._load_concepts()

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

    def _create_widgets(self) -> None:
        # Layout principal
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Cabeçalho instrutivo
        lbl_info = ttk.Label(
            main_frame,
            text="Revise e edite a lista de conceitos abaixo.\nEstes termos serão usados como rótulos nas matrizes.",
            font=("Segoe UI", 9),
            justify="left"
        )
        lbl_info.pack(fill="x", pady=(0, 10))

        # Container do meio (Lista + Botões)
        list_container = ttk.Frame(main_frame)
        list_container.pack(fill="both", expand=True, pady=5)

        # Treeview para exibir os conceitos de forma limpa
        self.tree = ttk.Treeview(list_container, columns=("name"), show="headings", selectmode="browse")
        self.tree.heading("name", text="Nome do Conceito", anchor="w")
        self.tree.column("name", minwidth=200, width=250, stretch=True)
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar para o Treeview
        scrollbar = ttk.Scrollbar(list_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Painel de ações laterais
        action_frame = ttk.Frame(main_frame, padding=(0, 10, 0, 0))
        action_frame.pack(fill="x")

        self.btn_add = ttk.Button(action_frame, text="Adicionar", command=self._add_concept)
        self.btn_add.pack(side="left", padx=2)

        self.btn_edit = ttk.Button(action_frame, text="Renomear", command=self._edit_concept)
        self.btn_edit.pack(side="left", padx=2)

        self.btn_remove = ttk.Button(action_frame, text="Remover", command=self._remove_concept)
        self.btn_remove.pack(side="left", padx=2)

        # Divisor
        ttk.Separator(main_frame, orient="horizontal").pack(fill="x", pady=10)

        # Botões de controle final na base
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", side="bottom")

        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        self.btn_cancel.pack(side="right", padx=5)

        self.btn_ok = ttk.Button(btn_frame, text="Confirmar", command=self._confirm)
        self.btn_ok.pack(side="right", padx=5)

        # Binds de atalhos e cliques
        self.tree.bind("<Double-1>", lambda e: self._edit_concept())
        self.tree.bind("<Delete>", lambda e: self._remove_concept())

    def _load_concepts(self) -> None:
        # Limpar
        for item in self.tree.get_children():
            self.tree.delete(item)
        # Recarregar
        for idx, concept in enumerate(self.concepts):
            self.tree.insert("", "end", iid=str(idx), values=(concept,))

    def _add_concept(self) -> None:
        new_name = simpledialog.askstring(
            "Adicionar Conceito",
            "Digite o nome do novo conceito:",
            parent=self
        )
        if new_name:
            new_name = new_name.strip()
            if not new_name:
                return
            if new_name in self.concepts:
                messagebox.showerror("Erro", f"O conceito '{new_name}' já existe.", parent=self)
                return
            self.concepts.append(new_name)
            self._load_concepts()
            # Seleciona o recém-criado
            new_id = str(len(self.concepts) - 1)
            self.tree.selection_set(new_id)
            self.tree.see(new_id)

    def _edit_concept(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um conceito para renomear.", parent=self)
            return
        
        idx = int(selected[0])
        old_name = self.concepts[idx]

        new_name = simpledialog.askstring(
            "Renomear Conceito",
            f"Renomear o conceito '{old_name}' para:",
            initialvalue=old_name,
            parent=self
        )
        if new_name:
            new_name = new_name.strip()
            if not new_name or new_name == old_name:
                return
            if new_name in self.concepts and self.concepts.index(new_name) != idx:
                messagebox.showerror("Erro", f"O conceito '{new_name}' já existe na lista.", parent=self)
                return
            
            self.concepts[idx] = new_name
            self._load_concepts()
            self.tree.selection_set(str(idx))

    def _remove_concept(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um conceito para remover.", parent=self)
            return
        
        idx = int(selected[0])
        name = self.concepts[idx]

        confirm = messagebox.askyesno(
            "Confirmar Remoção",
            f"Tem certeza que deseja remover o conceito '{name}'?\nIsso removerá a linha e a coluna correspondente desta matriz.",
            parent=self
        )
        if confirm:
            self.concepts.pop(idx)
            self._load_concepts()
            if self.concepts:
                next_sel = str(min(idx, len(self.concepts) - 1))
                self.tree.selection_set(next_sel)

    def _confirm(self) -> None:
        if not self.concepts:
            messagebox.showerror("Erro", "A matriz deve conter pelo menos 1 conceito.", parent=self)
            return
        self.confirmed = True
        self.on_confirm(self.concepts)
        # self.destroy()
