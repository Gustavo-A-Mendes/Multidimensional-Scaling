import tkinter as tk
from tkinter import ttk

# ============================================================
# COMBOBOX AND SPINBOX

window = tk.Tk()

window.geometry('600x400')
window.title('Combo and Spin')

# combobox:
items = ['Ice Cream', 'Pizza', 'Broccoli']
food_string = tk.StringVar(value=items[0])

combo = ttk.Combobox(window, textvariable=food_string)
combo['values'] = items
# combo.configure(values = items)
combo.pack()

# unique event for combobox:
combo.bind('<<ComboboxSelected>>', lambda event: print(combo_label.config(text=f'Selected value: {food_string.get()}')))

combo_label = ttk.Label(window, text='a label')
combo_label.pack()


# spinbox:
spin_int = tk.IntVar(value=12)
spin = ttk.Spinbox(
    window,
    from_=3,
    to=20,
    increment=3,
    command=lambda: print(spin_int.get()),
    textvariable=spin_int
)

# spin['values'] = (1, 2, 3, 4, 5)

# unique event for spinbox:
spin.bind('<<Increment>>', lambda event: print('up'))
spin.bind('<<Decrement>>', lambda event: print('down'))

spin.pack()

'''
EX4:    
    - Crie um spinbox que contenha as letras A B C D E
    - Imprima o valor sempre que o valor diminuir
'''
items2 = ('A', 'B', 'C', 'D', 'E')
spin2_string = tk.StringVar(value=items2[0])
spin2 = ttk.Spinbox(
    window,
    values=items2,
    textvariable=spin2_string
)
spin2.pack()

spin2.bind('<<Decrement>>', lambda e: print(spin2_string.get()))

# run
window.mainloop()

