import tkinter as tk
from tkinter import ttk
from random import randint, choice

# ============================================================
# SCROLLING

# setup:
window = tk.Tk()
window.geometry("600x400")
window.title("Scrolling")

# text:

text = tk.Text(window)
for i in range(1, 200):
    text.insert(f"{i}.0", f"text: {i}\n")
text.pack(expand=True, fill="both")

# scrollbar:
scrollbar_text = ttk.Scrollbar(window, orient="vertical", command=text.yview)
text.configure(yscrollcommand=scrollbar_text.set)
scrollbar_text.place(relx=1, rely=0, relheight=1, anchor="ne")

# run window:
window.mainloop()