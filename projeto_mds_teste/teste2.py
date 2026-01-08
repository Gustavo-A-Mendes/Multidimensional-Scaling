# # # # # import tkinter as tk
# # # # # from tkinter import ttk
# # # # #
# # # # # root = tk.Tk()
# # # # # root.title("Exemplo - Notebook")
# # # # # root.geometry("400x250")
# # # # #
# # # # # notebook = ttk.Notebook(root)
# # # # # notebook.pack(fill="both", expand=True)
# # # # #
# # # # # # --- Tabs (Frames) ---
# # # # # tab1 = ttk.Frame(notebook)
# # # # # tab2 = ttk.Frame(notebook)
# # # # #
# # # # # notebook.add(tab1, text="Aba 1")
# # # # # notebook.add(tab2, text="Aba 2")
# # # # #
# # # # # ttk.Label(tab1, text="Conteúdo da Aba 1").pack(pady=20)
# # # # # ttk.Label(tab2, text="Conteúdo da Aba 2").pack(pady=20)
# # # # #
# # # # # root.mainloop()
# # # #
# # # # import customtkinter as ctk
# # # #
# # # # ctk.set_appearance_mode("dark")
# # # #
# # # # root = ctk.CTk()
# # # # root.title("Exemplo - CTkTabview")
# # # # root.geometry("400x250")
# # # #
# # # # tabview = ctk.CTkTabview(root)
# # # # tabview.pack(fill="both", expand=True, padx=10, pady=10)
# # # #
# # # # # --- Tabs ---
# # # # tab1 = tabview.add("Aba 1")
# # # # tab2 = tabview.add("Aba 2")
# # # #
# # # # ctk.CTkLabel(tab1, text="Conteúdo da Aba 1").pack(pady=20)
# # # # ctk.CTkLabel(tab2, text="Conteúdo da Aba 2").pack(pady=20)
# # # #
# # # # root.mainloop()
# # #
# # # import tkinter as tk
# # #
# # # root = tk.Tk()
# # # root.title("Exemplo - Tabs (manual)")
# # # root.geometry("400x250")
# # #
# # # # Container onde os frames serão trocados
# # # container = tk.Frame(root)
# # # container.pack(fill="both", expand=True)
# # #
# # # # --- Duas "tabs" (frames) ---
# # # tab1 = tk.Frame(container, bg="#d0e0ff")
# # # tab2 = tk.Frame(container, bg="#ffd0d0")
# # #
# # # for frame in (tab1, tab2):
# # #     frame.place(relx=0, rely=0, relwidth=1, relheight=1)
# # #
# # # # Conteúdo das tabs
# # # tk.Label(tab1, text="Conteúdo da Aba 1").pack(pady=40)
# # # tk.Label(tab2, text="Conteúdo da Aba 2").pack(pady=40)
# # #
# # # # Função de mudar aba
# # # def show_tab(frame):
# # #     frame.lift()   # traz o frame para frente
# # #
# # # # Botões para simular abas
# # # tk.Button(root, text="Mostrar Aba 1", command=lambda: show_tab(tab1)).pack(side="left", fill="x", expand=True)
# # # tk.Button(root, text="Mostrar Aba 2", command=lambda: show_tab(tab2)).pack(side="left", fill="x", expand=True)
# # #
# # # # Começa com Aba 1
# # # show_tab(tab1)
# # #
# # # root.mainloop()
# #
# # import tkinter as tk
# # from tkinter import ttk
# #
# # root = tk.Tk()
# # root.geometry("400x250")
# #
# # tree = ttk.Treeview(root)
# #
# # # Colunas da tabela
# # tree["columns"] = ("A", "B", "C")
# #
# # # Configurar headings das colunas
# # for col in tree["columns"]:
# #     tree.heading(col, text=col)
# #     tree.column(col, width=80, anchor="center")
# #
# # # Configurar a coluna #0 para os nomes das linhas
# # tree.heading("#0", text="Linha")
# # tree.column("#0", width=100, anchor="center")
# #
# # # Exemplo de dados
# # nomes_linhas = ["X1", "X2", "X3"]
# # dados = [
# #     [1, 2, 3],
# #     [4, 5, 6],
# #     [7, 8, 9]
# # ]
# #
# # # Inserir dados
# # for nome, linha in zip(nomes_linhas, dados):
# #     tree.insert("", "end", text=nome, values=linha)
# #
# # tree.pack(fill="both", expand=True)
# # root.mainloop()
#
#
# import tkinter as tk
# from tkinter import ttk
#
# root = tk.Tk()
# root.geometry("400x300")
#
# style = ttk.Style()
# style.configure("Treeview",
#                 rowheight=35,
#                 font=("Segoe UI", 10),
#                 padding=(5,5),
#                 relief="solid",
#                 borderwidth=1)
# style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
#
# tree = ttk.Treeview(root, show="tree headings")
# tree.pack(fill="both", expand=True)
#
# cols = ["A", "B", "C"]
# tree["columns"] = cols
# tree.heading("#0", text="Linha")
# tree.column("#0", width=80, anchor="center")
#
# for col in cols:
#     tree.heading(col, text=col)
#     tree.column(col, width=80, anchor="center")
#
# # Inserir dados com cores alternadas
# data = [
#     [1,2,3],
#     [4,5,6],
#     [7,8,9]
# ]
# for i, row in enumerate(data):
#     cor = "#f0f0f0" if i % 2 == 0 else "#ffffff"
#     tree.insert("", "end", text=f"L{i+1}", values=row, tags=(cor,))
# tree.tag_configure("#f0f0f0", background="#f0f0f0")
# tree.tag_configure("#ffffff", background="#ffffff")
#
# root.mainloop()


from tksheet import Sheet
import tkinter as tk

root = tk.Tk()

data = [
    [1, 2, 3],
    [4, 5, 6],
]

sheet = Sheet(root, data=data)
sheet.pack(fill="both", expand=True)

# Estilizar células
sheet.highlight_cells(row=0, column=1, bg="yellow", fg="red")

root.mainloop()
