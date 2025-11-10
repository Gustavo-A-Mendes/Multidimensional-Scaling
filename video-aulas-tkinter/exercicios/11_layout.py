import tkinter as tk
from tkinter import ttk

# ============================================================
# LAYOUT

window = tk.Tk()
window.geometry("600x400")
window.title("Layout intro")

# widgets:
label1 = ttk.Label(window, text="Label 1", background="red")
label2 = ttk.Label(window, text="Label 2", background="blue")

# # pack:
# label1.pack(side="left", expand=True, fill="y")
# label2.pack(side="left", expand=True, fill="both")

# grid:
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=2)
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)

label1.grid(row=0, column=1, sticky="news")
label2.grid(row=1, column=1, columnspan=2, sticky="news")

# # place:
# label1.place(x=100, y=300, width=200, height=100)
# label2.place(relx=0.5, rely=0.5, relwidth=0.3, anchor="se")

# run:
window.mainloop()