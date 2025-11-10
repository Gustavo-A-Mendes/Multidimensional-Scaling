import tkinter as tk
from tkinter import ttk

# ============================================================
# TABS

window = tk.Tk()
window.geometry("600x400")
window.title("Tab Widget")

# Notebook widget:
notebook = ttk.Notebook(window)

# tab 1:
tab1 = ttk.Frame(notebook, width=200, height=400)
label1 = ttk.Label(tab1, text="Text in tab 1")
label1.pack()
button1 = ttk.Button(tab1, text="Button in tab 1")
button1.pack()

# tab 2
tab2 = ttk.Frame(notebook)
label2 = ttk.Label(tab2, text="Text in tab 2")
label2.pack()
entry2 = ttk.Entry(tab2)
entry2.pack()

notebook.add(tab1, text="Tab 1")
notebook.add(tab2, text="Tab 2")
notebook.pack()

'''
EX7:    
    - Adicione outro tab com 2 botões e um label dentro
'''

# tab 3:
tab3 = ttk.Frame(notebook)
button3a = ttk.Button(tab3, text="Button A")
button3b = ttk.Button(tab3, text="Button B")
button3a.pack()
button3b.pack()

label3 = ttk.Label(tab3, text="Text in tab 3")
label3.pack()

notebook.add(tab3, text="Tab 3")

# run:
window.mainloop()