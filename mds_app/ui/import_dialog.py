import tkinter as tk
from tkinter import ttk
from tkinter import simpledialog, messagebox

class ImportDialog(tk.Toplevel):
    def __init__(self, parent, headers, on_confirm):
        super().__init__(parent)
        self.parent = parent
        self.title("Revisão de Cabeçalhos")
        self.geometry("400x250")

        # self.update_idletasks()
        # self.bind("<Configure>", lambda e: print(self.winfo_width(), self.winfo_height()))

        self.transient(parent)  # fica "presa" à janela pai
        self.grab_set()  # bloqueia interação com outras janelas
        self.focus_set()  # foco imediato

        self.headers = headers
        self.on_confirm = on_confirm
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()

    # create a listbox and its own frame:
    @staticmethod
    def _create_listbox(parent):
        frame = ttk.Frame(parent)

        lb = tk.Listbox(frame, selectmode="extended")
        sb = ttk.Scrollbar(frame, orient="vertical", command=lb.yview)
        lb.config(yscrollcommand=sb.set)

        lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        return frame, lb

    # create a dual list import dialog:
    def _create_widgets(self):
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # main frame:
        main = ttk.Frame(self)

        main.columnconfigure((0, 4), weight=1)
        main.columnconfigure(1, weight=0)

        # listbox frame:
        left_frame, self.lb_available = self._create_listbox(main)
        right_frame, self.lb_selected = self._create_listbox(main)

        # control frame:
        controls = ttk.Frame(main)

        # buttons:
        self.btn_move_selected = ttk.Button(controls, text=">", command=self._move_selected, state="disabled")
        self.btn_move_all = ttk.Button(controls, text=">>", command=self._move_all)
        self.btn_return_selected = ttk.Button(controls, text="<", command=self._return_selected, state="disabled")
        self.btn_return_all = ttk.Button(controls, text="<<", command=self._return_all)
        self.btn_confirm = ttk.Button(self, text="Confirmar", command=self._confirm)

        # ----------------------------------------------------------------------
        # configure event binds:
        # ----------------------------------------------------------------------
        self.lb_available.bind("<<ListboxSelect>>", self._on_available_select)
        self.lb_selected.bind("<<ListboxSelect>>", self._on_selected_select)

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------
        main.pack(fill="both", expand=True, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky="nsew")
        right_frame.grid(row=0, column=2, sticky="nsew")
        controls.grid(row=0, column=1, padx=10)
        self.btn_move_selected.pack(pady=2)
        self.btn_move_all.pack(pady=2)
        self.btn_return_selected.pack(pady=2)
        self.btn_return_all.pack(pady=2)
        self.btn_confirm.pack(side="right", padx=10, pady=10)

        # ----------------------------------------------------------------------
        # filling listbox:
        # ----------------------------------------------------------------------
        self.lb_available.delete(0, "end")
        self.lb_selected.delete(0, "end")

        for h in self.headers:
            self.lb_available.insert("end", h)

    # setting between dual list:
    def _move_selected(self):
        items = [self.lb_available.get(i) for i in self.lb_available.curselection()]
        for item in items:
            # self._insert_unique(self.lb_selected, item)
            self.lb_selected.insert("end", item)
        for i in reversed(self.lb_available.curselection()):
            self.lb_available.delete(i)
        self.btn_move_selected.config(state="disabled")

    def _move_all(self):
        items = self.lb_available.get(0, "end")
        for item in items:
            # self._insert_unique(self.lb_selected, item)
            self.lb_selected.insert("end", item)
        self.lb_available.delete(0, "end")
        self.btn_move_selected.config(state="disabled")

    def _return_selected(self):
        items = [self.lb_selected.get(i) for i in self.lb_selected.curselection()]
        for item in items:
            # self._insert_unique(self.lb_available, item)
            self.lb_available.insert("end", item)
        for i in reversed(self.lb_selected.curselection()):
            self.lb_selected.delete(i)
        self.btn_return_selected.config(state="disabled")

    def _return_all(self):
        items = self.lb_selected.get(0, "end")
        for item in items:
            # self._insert_unique(self.lb_available, item)
            self.lb_available.insert("end", item)
        self.lb_selected.delete(0, "end")
        self.btn_return_selected.config(state="disabled")

    def _on_available_select(self, event):
        if self.lb_available.curselection():
            self.btn_move_selected.config(state="normal")
        else:
            self.btn_move_selected.config(state="disabled")

    def _on_selected_select(self, event):
        if self.lb_selected.curselection():
            self.btn_return_selected.config(state="normal")
        else:
            self.btn_return_selected.config(state="disabled")

    def _validate(self):
        if self.lb_selected.size() == 0:
            messagebox.showerror(
                "Erro",
                "A lista de itens selecionados não pode estar vazia."
            )
            return False
        return True

    def _confirm(self):
        if not self._validate():
            return

        selected = self.lb_selected.get(0, "end")
        # self.parent.btn_mds.config(state="normal")
        self.parent.control_panel.view = "data"

        self.on_confirm(selected)
        self.grab_release()
        self.destroy()

    def _on_close(self):
        self.grab_release()
        self.destroy()

    # not applied methods
    def _move_up(self):
        selection = self.lb_selected.curselection()
        if not selection:
            return

        i = selection[0]
        if i == 0:
            return

        item = self.lb_selected.get(i)
        self.lb_selected.delete(i)
        self.lb_selected.insert(i - 1, item)
        self.lb_selected.selection_set(i - 1)

    def _move_down(self):
        selection = self.lb_selected.curselection()
        if not selection:
            return

        i = selection[0]
        if i == self.lb_selected.size() - 1:
            return

        item = self.lb_selected.get(i)
        self.lb_selected.delete(i)
        self.lb_selected.insert(i + 1, item)
        self.lb_selected.selection_set(i + 1)

    def _edit_item(self):
        lb = self._get_active_listbox()
        if not lb:
            return

        selection = lb.curselection()
        if len(selection) != 1:
            messagebox.showwarning("Aviso", "Selecione apenas um item para editar.")
            return

        i = selection[0]
        old_value = lb.get(i)

        new_value = simpledialog.askstring(
            "Editar",
            "Novo valor:",
            initialvalue=old_value,
            parent=self
        )

        if new_value:
            lb.delete(i)
            lb.insert(i, new_value.strip())
            lb.selection_set(i)

    def _add_item(self):
        from tkinter import simpledialog

        value = simpledialog.askstring(
            "Adicionar",
            "Digite o novo valor:",
            parent=self
        )

        if value:
            value = value.strip()
            if value not in self.lb_available.get(0, "end"):
                self.lb_available.insert("end", value)

    def _remove_item(self):
        lb = self._get_active_listbox()
        if not lb:
            return

        for i in reversed(lb.curselection()):
            lb.delete(i)

    @staticmethod
    def _insert_unique(listbox, item):
        if item not in listbox.get(0, "end"):
            listbox.insert("end", item)
            return True
        return False

    def _get_active_listbox(self):
        if self.lb_available.curselection():
            return self.lb_available
        if self.lb_selected.curselection():
            return self.lb_selected
        return None
