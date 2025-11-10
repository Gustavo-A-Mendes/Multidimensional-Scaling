import tkinter as tk
from tkinter import ttk

# ============================================================
# MENU

window = tk.Tk()
window.geometry("600x400")
window.title("Menu")

# menu:
menu = tk.Menu(window)

# sub menu:
file_menu = tk.Menu(menu, tearoff=False)
file_menu.add_command(label="New", command=lambda: print("New file"))
file_menu.add_command(label="Open", command=lambda: print("Open file"))
file_menu.add_separator()
menu.add_cascade(label="File", menu=file_menu)

# anothe sub menu:
help_menu = tk.Menu(menu, tearoff=False)
help_menu.add_command(label="Help entry", command=lambda: print(help_check_string.get()))

help_check_string = tk.StringVar()
help_menu.add_checkbutton(label="check", onvalue="on", offvalue="off", variable=help_check_string)

menu.add_cascade(label="Help", menu=help_menu)

window.configure(menu=menu)

# menu button:
menu_button = ttk.Menubutton(window, text="Menu Button")
menu_button.pack()

button_sub_menu = tk.Menu(menu_button, tearoff=False)
button_sub_menu.add_cascade(label="entry 1", command=lambda: print("test 1"))
button_sub_menu.add_checkbutton(label="check 1")

menu_button.configure(menu=button_sub_menu)

'''
EX8:    
    - Adicione outro menu no Menu Principal, esse deve ter um sub menu
    - Tente ler o website abaixo e adicione um submenu
    - docs: https://www.tutorialspoint.com/python/tk_menu.htm
'''

# new sub menu:
exercise_menu = tk.Menu(menu, tearoff=False)
exercise_menu.add_command(label="test 1", command=lambda: print("test 1"))
exercise_menu.add_command(label="test 2", command=lambda: print("test 2"))
exercise_menu.add_command(label="test 3", command=lambda: print("test 3"))

# sub sub menu:
exercise_sub_menu = tk.Menu(exercise_menu, tearoff=False)
exercise_sub_menu.add_command(label="sub test 1", command=lambda: print("sub test 1"))
exercise_sub_menu.add_command(label="sub test 2", command=lambda: print("sub test 2"))
exercise_sub_menu.add_command(label="sub test 3", command=lambda: print("sub test 3"))


exercise_menu.add_cascade(label="Exercise sub menu", menu=exercise_sub_menu)

menu.add_cascade(label="Exercise menu", menu=exercise_menu)

# run:
window.mainloop()