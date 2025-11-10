import tkinter as tk
from tkinter import ttk

# ============================================================
# TKINTER VARIABLES

window = tk.Tk()

'''
EX1:    
    - Criar 2 campos de Entry e 1 Label, que devem 
      estar todas conectadas via StringVar
    
    - Iniciar com valor inicial de 'test'
'''

window.title('Exercício 01')

string_var = tk.StringVar(value='test')
# string_var.set('test')

entry1 = ttk.Entry(master=window, textvariable=string_var)
entry1.pack(pady=10)

entry2 = ttk.Entry(master=window, textvariable=string_var)
entry2.pack(pady=10)

label = ttk.Label(master=window, text='', textvariable=string_var)
label.pack(pady=10)

window.mainloop()