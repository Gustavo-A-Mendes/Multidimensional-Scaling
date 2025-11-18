import tkinter as tk
from tkinter import ttk, font

# ============================================================
# STYLING METHODS

# window:
window = tk.Tk()
window.title("Styling")
window.geometry("400x300")

# print(font.families())

# style:
style = ttk.Style()
# print(style.theme_names())
# style.theme_use('classic')
style.configure(
    "new.TButton",
    foreground="green",
    font=("System", 20)
)
style.map(
    "new.TButton",
    foreground=[('pressed', 'red'), ('disabled', 'yellow'), ('hover', 'blue')],
    background=[('pressed', 'green'), ('active', 'blue')]
)

style.configure(
    "new.TFrame",
    background="pink",
)

# widgets:
label = ttk.Label(
    window,
    text="A label\nAnd the type on another line",
    background='red',
    foreground='white',
    font=("System", 20),
    justify= "left"
)
label.pack(expand=True, fill="both")

button = ttk.Button(
    window,
    text="A button",
    style = 'new.TButton'
    # state="disabled"
)
button.pack()

""" 
    EX15:
        - Adicione um frame com uma largura e altura e ponha um background "pink" (rosa)
"""

frame = ttk.Frame(
    window,
    height=200,
    width=100,
    style="new.TFrame"
)
frame.pack()

# run:
window.mainloop()