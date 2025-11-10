import tkinter as tk
from tkinter import ttk
from random import randint, choice

# ============================================================
# SCROLLING

# setup:
window = tk.Tk()
window.geometry("600x400")
window.title("Scrolling")

# treeview:
table = ttk.Treeview(window, columns = (1, 2, 3), show="headings")
table.heading(1, text="ID")
table.heading(2, text="Last Name")
table.heading(3, text="Last Name")
first_names = ['Bob', 'Maria', 'Alex', 'James', 'Susan', 'Henry', 'Lisa', 'Anna', 'Lisa']
last_names = ['Smith', 'Brown', 'Wilson', 'Thomson', 'Cook', 'Taylor', 'Walker', 'CLark']
for i in range(1000):
    table.insert(parent='', index=tk.END, values=(i+1, choice(first_names), choice(last_names)))
table.pack(expand=True, fill="both")

# scrollbar:
scrollbar_table = ttk.Scrollbar(window, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar_table.set)
scrollbar_table.place(relx=1, rely=0, relheight=1, anchor="ne")


# run window:
window.mainloop()