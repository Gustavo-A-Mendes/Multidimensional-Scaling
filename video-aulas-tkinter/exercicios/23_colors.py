import tkinter as tk
from tkinter import ttk

# ============================================================
# COLORS

# window:
window = tk.Tk()
window.title('Colors')
window.geometry('400x300')

# widgets:
ttk.Label(window, background="red").pack(expand=True, fill="both")
ttk.Label(window, background="#00f").pack(expand=True, fill="both")
ttk.Label(window, background="#4fc296").pack(expand=True, fill="both")

""" 
    EX16:
        - Crie uma cor "amarronzada" usando valores hexadecimais
        - Crie a cor branca usando valores hexadecimais
        - Crie a cor preto usando valores hexadecimais
"""

ttk.Label(window, background="#4a2e10").pack(expand=True, fill="both")
ttk.Label(window, background="#ffffff").pack(expand=True, fill="both")
ttk.Label(window, background="#000000").pack(expand=True, fill="both")
ttk.Label(window, background="#666666").pack(expand=True, fill="both")

# run:
window.mainloop()