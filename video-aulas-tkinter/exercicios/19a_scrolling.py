import tkinter as tk
from tkinter import ttk
from random import randint, choice

# ============================================================
# SCROLLING

# setup:
window = tk.Tk()
window.geometry("600x400")
window.title("Scrolling")

# canvas:
canvas = tk.Canvas(window, bg="white", scrollregion=(0, 0, 2000, 5000))
canvas.create_line(0, 0, 2000, 5000, fill="green", width=10)
for _ in range(100):
    l = randint(0, 2000)
    t = randint(0, 5000)
    r = l + randint(10, 500)
    b = t + randint(10, 500)
    color = choice(["red", "green", "blue", "yellow", "orange"])
    canvas.create_rectangle(l, t, r, b, fill=color)
canvas.pack(expand=True, fill="both")

# mousewheel scrolling:
canvas.bind("<MouseWheel>", lambda event: canvas.yview_scroll(-int(event.delta/60), "units"))


# scrollbars:
"""
    Para vincular a scrollbar a um canvas, é necessário configurar o comando
    da scrollbar para o método de visualização do canvas (xview ou yview),
    e configurar o canvas para atualizar a scrollbar através dos parâmetros
    xscrollcommand e yscrollcommand.
"""
scrollbar_v = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar_v.set)
scrollbar_v.place(relx=1, rely=0, relheight=1, anchor="ne")

'''
EX13a:    
    - Crie um scrolbar horizontal, na base da tela e use para dar scroll no canva para esquerda e direita
    - Adicione também um evento para o scroll com o mouse (Ctrl + scroll do mouse)
'''

scrollbar_h = ttk.Scrollbar(window, orient="horizontal", command=canvas.xview)
canvas.configure(xscrollcommand=scrollbar_h.set)
scrollbar_h.place(relx=0, rely=1, relwidth=1, anchor="sw")

# mousewheel horizontal scrolling with Ctrl:
canvas.bind('<Control-MouseWheel>', lambda event: canvas.xview_scroll(-int(event.delta/60), "units"))


# run window:
window.mainloop()