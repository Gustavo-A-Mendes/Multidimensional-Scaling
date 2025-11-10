import tkinter as tk
from tkinter import ttk

# ============================================================
# TKINTER BUTTONS

window = tk.Tk()
window.title('buttons')
window.geometry('600x400')

# buttons
def button_func():
    print('a basic button')
    print(radio_var.get())

button_string = tk.StringVar(value='A button with string var')
button = ttk.Button(window, text='A simple button', command= button_func, textvariable=button_string)
button.pack()

# check buttons
check_var = tk.IntVar()
check1 = ttk.Checkbutton(
    window, 
    text='checkbox 1',
    command=lambda: check_var.set(10),
    variable=check_var,
    onvalue=10,
    offvalue=5
)
check1.pack()

check2 = ttk.Checkbutton(
    window, 
    text='checkbox 2',
    command=lambda: check_var.set(5),
    variable=check_var,
    onvalue=5,
    offvalue=10
)
check2.pack()

# radio buttons
radio_var = tk.StringVar()
radio1 = ttk.Radiobutton(
    window,
    text='Radiobutton 1',
    value=1,
    variable=radio_var,
    command=lambda: print(radio_var.get())
)
radio1.pack()
radio2 = ttk.Radiobutton(
    window,
    text='Radiobutton 2',
    value=2,
    variable=radio_var     
)
radio2.pack()

'''
EX2:    
    - Criar um checkbutton e 2 radiobuttons

        1. radio button:
             - valores dos botões são A e B
             - selecionar imprime o valor do checkbutton
             - selecionar um radiobutton desseleciona o checkbutton
        
        2. check button:
            - selecionar o checkbutton imprime o valor do radiobutton selecionado
            - use a variável do tkinter para Booleans
      estar todas conectadas via StringVar
    
    - Iniciar com valor inicial de 'test'
'''

def radio_func():
    print(check_bool.get())
    check_bool.set(False)

# data
radio_string = tk.StringVar()
check_bool = tk.BooleanVar()

# widgets:
radio1 = ttk.Radiobutton(window, text='Radio A', value='A', command= radio_func, variable=radio_string)
radio2 = ttk.Radiobutton(window, text='Radio B', value='B', command= radio_func, variable=radio_string)

check = ttk.Checkbutton(window, text='exercise check', variable=check_bool, command=lambda: print(radio_string.get()))

# layout
radio1.pack()
radio2.pack()
check.pack()

# run
window.mainloop()

