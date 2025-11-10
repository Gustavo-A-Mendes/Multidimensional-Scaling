import tkinter as tk
from tkinter import ttk

# ============================================================
# FUNCTIONS WITH ARGUMENTS

window = tk.Tk()
window.title('buttons, functions and arguments')


# widgets:
entry_string = tk.StringVar(value='test')
entry = ttk.Entry(window, textvariable=entry_string)
entry.pack()

# método 1: envelopando a função com um método lambda
def button_func(entry_string):
    print('the button1 was pressed')
    print(entry_string.get())

button1 = ttk.Button(window, text='button método 1', command= lambda: button_func(entry_string))
button1.pack()

# método 2: outer_func retornando função interna:
def outer_func(parameter):
    def inner_func():
        print('the button2 was pressed')
        print(parameter.get())
    
    return inner_func

button2 = ttk.Button(window, text='button método 2', command=outer_func(entry_string))
button2.pack()

# run
window.mainloop()