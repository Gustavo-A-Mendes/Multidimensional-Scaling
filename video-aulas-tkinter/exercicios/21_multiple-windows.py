import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# ============================================================
# MULTIPLE WINDOWS

class Extra(tk.Toplevel):
    def __init__(self):
        super().__init__()
        self.title("extra window")
        self.geometry("300x400")
        ttk.Label(self, text="A label").pack()
        ttk.Button(self, text="A button").pack()
        ttk.Label(self, text="Another label").pack(expand=True)

# https://docs.python.org/3/library/tkinter.messagebox.html

def ask_yes_no():
    # answer = messagebox.askquestion("Title", "body")
    # print(answer)
    answer = messagebox.showinfo("Some information", "Here is some information")
    print(answer)

def create_window():
    global extra_window
    extra_window = Extra()
    # extra_windows = tk.Toplevel()
    # extra_windows.title("extra window")
    # extra_windows.geometry("300x400")
    # ttk.Label(extra_windows, text="A label").pack()
    # ttk.Button(extra_windows, text="A button").pack()
    # ttk.Label(extra_windows, text="Another label").pack(expand=True)

def close_window():
    extra_window.destroy()

window = tk.Tk()
window.geometry("600x400")
window.title("Multiple windows")

button1 = ttk.Button(window, text='open main window', command=create_window)
button1.pack(expand=True)

button2 = ttk.Button(window, text='close main window', command=close_window)
button2.pack(expand=True)

button3 = ttk.Button(window, text='create yes no window', command=ask_yes_no)
button3.pack(expand=True)

# message box:


# toplevel:


# run:
window.mainloop()