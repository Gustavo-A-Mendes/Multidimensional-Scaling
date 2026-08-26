import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class ConceptManagerWindow(tk.Toplevel):
    def __init__(self, parent, concepts: list[str], on_confirm, title: str = "Gerenciar Conceitos") -> None:
        super().__init__(parent)

        self.withdraw() # Oculta a janela durante a inicialização
        
        self.parent = parent
        self.title(title)
        self.geometry("600x450")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.focus_set()

        self.concepts = [[c, c] for c in concepts]
        self.concepts_history = list(concepts)
        self.inactive_concepts = []
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

        # Exibe a janela
        self.deiconify()

    def _create_widgets(self) -> None:
        # Layout principal
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill="both", expand=True)

        # Cabeçalho instrutivo
        lbl_info = ttk.Label(
            main_frame,
            text="Revise e edite os conceitos. Os conceitos ativos serão usados como rótulos nas matrizes.\n"
                 "Os conceitos desativados não serão usados e serão excluídos ao confirmar.\n",
            font=("Segoe UI", 9),
            justify="left"
        )
        lbl_info.pack(side="top", fill="x", pady=(0, 10))

        # Botões de controle final na base (empacotados primeiro no bottom para evitar esmagamento)
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x", side="bottom")

        self.btn_cancel = ttk.Button(btn_frame, text="Cancelar", command=self.destroy)
        self.btn_cancel.pack(side="right", padx=5)

        self.btn_ok = ttk.Button(btn_frame, text="Confirmar", command=self._confirm)
        self.btn_ok.pack(side="right", padx=5)

        # Divisor
        sep = ttk.Separator(main_frame, orient="horizontal")
        sep.pack(fill="x", side="bottom", pady=10)

        # Legenda explicativa para conceitos novos
        lbl_legend = ttk.Label(
            main_frame,
            text="* conceitos criados nesta sessão.\n"
                 "Fechar sem confirmar, os conceitos serão descartados.",
            font=("Segoe UI", 9, "italic"),
            foreground="#856404",
            justify="left"
        )
        lbl_legend.pack(fill="x", side="bottom", pady=(5, 5))

        # Container das duas listas side-by-side (empacotado por último com expand=True para ocupar o centro)
        lists_frame = ttk.Frame(main_frame)
        lists_frame.pack(fill="both", expand=True, pady=5)

        # 1. Painel da esquerda (Inativos / Disponíveis)
        left_frame = ttk.Frame(lists_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        ttk.Label(left_frame, text="Conceitos Inativos", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))
        
        left_tree_container = ttk.Frame(left_frame)
        left_tree_container.pack(fill="both", expand=True)

        self.left_tree = ttk.Treeview(left_tree_container, columns=("name"), show="headings", selectmode="browse")
        # self.left_tree.heading("name", text="Nome do Conceito", anchor="w")
        self.left_tree.column("name", minwidth=150, width=180, stretch=True)
        self.left_tree.pack(side="left", fill="both", expand=True)

        scrollbar_left = ttk.Scrollbar(left_tree_container, orient="vertical", command=self.left_tree.yview)
        scrollbar_left.pack(side="right", fill="y")
        self.left_tree.configure(yscrollcommand=scrollbar_left.set)
        
        # 2. Painel da direita (Ativos)
        right_frame = ttk.Frame(lists_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        ttk.Label(right_frame, text="Conceitos Ativos", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 5))

        right_tree_container = ttk.Frame(right_frame)
        right_tree_container.pack(fill="both", expand=True)

        self.right_tree = ttk.Treeview(right_tree_container, columns=("name",), show="headings", selectmode="browse")
        # self.right_tree.heading("name", text="Nome do Conceito", anchor="w")
        self.right_tree.column("name", minwidth=150, width=180, stretch=True)
        self.right_tree.pack(side="left", fill="both", expand=True)

        scrollbar_right = ttk.Scrollbar(right_tree_container, orient="vertical", command=self.right_tree.yview)
        scrollbar_right.pack(side="right", fill="y")
        self.right_tree.configure(yscrollcommand=scrollbar_right.set)

        # 3. Painel do meio (Botões de transferência)
        middle_frame = ttk.Frame(lists_frame, padding=10)
        middle_frame.pack(fill="y", expand=False)

        self.btn_activate = ttk.Button(middle_frame, text="Ativar >>", width=12, command=self._activate_concept)
        self.btn_activate.pack(pady=5)

        self.btn_deactivate = ttk.Button(middle_frame, text="<< Desativar", width=12, command=self._deactivate_concept)
        self.btn_deactivate.pack(pady=5)

        self.btn_add = ttk.Button(middle_frame, text="Novo", width=12, command=self._add_concept)
        self.btn_add.pack(pady=5)

        self.btn_edit = ttk.Button(middle_frame, text="Renomear", width=12, command=self._edit_concept)
        self.btn_edit.pack(pady=5)

        # Configurar estilos de tags para Treeview (correção para o Windows)
        style = ttk.Style()
        style.map("Treeview",
                  background=[("selected", "#0078d7")],
                  foreground=[("selected", "white")])
        self.right_tree.tag_configure("new_concept", background="#fff2cc", foreground="#000000")

        # Binds de atalhos e cliques
        self.left_tree.bind("<Double-1>", lambda e: self._activate_concept())
        self.right_tree.bind("<Double-1>", lambda e: self._edit_concept())
        self.right_tree.bind("<Delete>", lambda e: self._deactivate_concept())

    def _load_concepts(self) -> None:
        # Limpar
        for item in self.left_tree.get_children():
            self.left_tree.delete(item)
        for item in self.right_tree.get_children():
            self.right_tree.delete(item)

        # Calcular conceitos inativos (originais que não estão atualmente ativos)
        active_originals = [c[1] for c in self.concepts if c[1] is not None]
        self.inactive_concepts = [c for c in self.concepts_history if c not in active_originals]

        # Recarregar lista da esquerda (inativos)
        for idx, concept in enumerate(self.inactive_concepts):
            self.left_tree.insert("", "end", iid=f"inactive_{idx}", values=(concept,))

        # Recarregar lista da direita (ativos)
        for idx, (current_name, original_name) in enumerate(self.concepts):
            if original_name is None:
                display_name = f"* {current_name}"
                self.right_tree.insert("", "end", iid=f"active_{idx}", values=(display_name,), tags=("new_concept",))
            else:
                self.right_tree.insert("", "end", iid=f"active_{idx}", values=(current_name,))

    def _activate_concept(self) -> None:
        selected = self.left_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um conceito disponível para ativar.", parent=self)
            return

        item_id = selected[0]
        print(item_id)
        idx = int(item_id.split("_")[1])
        concept_name = self.inactive_concepts[idx]

        # Mover para ativos (recupera original_name = concept_name)
        self.concepts.append([concept_name, concept_name])
        self._load_concepts()

        # Selecionar o recém-ativado na lista da direita
        new_active_idx = len(self.concepts) - 1
        self.right_tree.selection_set(f"active_{new_active_idx}")
        self.right_tree.see(f"active_{new_active_idx}")

    def _deactivate_concept(self) -> None:
        selected = self.right_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um conceito ativo para desativar.", parent=self)
            return

        item_id = selected[0]
        idx = int(item_id.split("_")[1])
        current_name, original_name = self.concepts[idx]

        confirm = messagebox.askyesno(
            "Confirmar Desativação",
            f"Tem certeza que deseja desativar o conceito '{current_name}'?\n"
            "Isso removerá a linha e a coluna correspondente desta matriz.",
            parent=self
        )
        if not confirm:
            return

        # Remover da lista de ativos
        self.concepts.pop(idx)
        self._load_concepts()

        # Selecionar outro item na lista da direita
        if self.concepts:
            next_sel = f"active_{min(idx, len(self.concepts) - 1)}"
            self.right_tree.selection_set(next_sel)

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

            if any(new_name == c[0] for c in self.concepts):
                messagebox.showerror("Erro", f"O conceito '{new_name}' já está ativo.", parent=self)
                return

            # Se existia no histórico e estava inativo, ativa-o (recupera dados originais)
            if new_name in self.inactive_concepts:
                self.concepts.append([new_name, new_name])
            else:
                self.concepts.append([new_name, None]) # Novo conceito
            
            self._load_concepts()
            new_active_idx = len(self.concepts) - 1
            self.right_tree.selection_set(f"active_{new_active_idx}")
            self.right_tree.see(f"active_{new_active_idx}")

    def _edit_concept(self) -> None:
        selected = self.right_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um conceito ativo para renomear.", parent=self)
            return
        
        idx = int(selected[0].split("_")[1])
        old_name = self.concepts[idx][0]

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

            if any(new_name == c[0] for i, c in enumerate(self.concepts) if i != idx):
                messagebox.showerror("Erro", f"O conceito '{new_name}' já está ativo.", parent=self)
                return
            
            # Se o novo nome está nos inativos, recupera seu histórico
            if new_name in self.inactive_concepts:
                self.concepts[idx][0] = new_name
                self.concepts[idx][1] = new_name
            else:
                # Caso contrário, apenas altera o nome de exibição
                self.concepts[idx][0] = new_name
            
            self._load_concepts()
            self.right_tree.selection_set(f"active_{idx}")

    def _confirm(self) -> None:
        if not self.concepts:
            messagebox.showerror("Erro", "A matriz deve conter pelo menos 1 conceito ativo.", parent=self)
            return
        self.confirmed = True

        concepts_tuple = [tuple(c) for c in self.concepts]
        self.on_confirm(concepts_tuple)
