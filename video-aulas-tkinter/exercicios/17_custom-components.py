import tkinter as tk
from tkinter import ttk

# ============================================================
# CUSTOM COMPONENTS WITH CLASSES AND FUNCTIONS 

def create_segment(master, label_text, button_text):
    frame = ttk.Frame(master)

    # grid layout:
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure((0, 1, 2), weight=1, uniform='a')

    # widgets:
    ttk.Label(frame, text=label_text).grid(row=0, column=0, sticky="news")
    ttk.Button(frame, text=button_text).grid(row=0, column=1, sticky="news")
                                         
    return frame


class Segment(ttk.Frame):
    def __init__(self, master, label_text, button_text, exercise_button_text):
        super().__init__(master)

        # grid layout:
        self.rowconfigure(0, weight=1)
        self.columnconfigure((0, 1, 2), weight=1, uniform='a')

        ttk.Label(self, text=label_text).grid(row=0, column=0, sticky="news")
        ttk.Button(self, text=button_text).grid(row=0, column=1, sticky="news")

        inner_segment = self.create_inner_segment(exercise_button_text)
        inner_segment.grid(row=0, column=2, sticky="news")

        self.pack(expand=True, fill="both", pady=10, padx=10)

    def create_inner_segment(self, button_text):
        
        inner_frame = ttk.Frame(self)

        ttk.Entry(inner_frame).pack(side="top", expand=True, fill="both")
        ttk.Button(inner_frame, text=button_text).pack(side="top", expand=True, fill="both")

        return inner_frame


# window:
window = tk.Tk()
window.title("Widget and return")
window.geometry("400x600")

# widgets with class:
Segment(window, "label", "button", "test")
Segment(window, "test", "click", "something else")
Segment(window, "hello", "test", "123")
Segment(window, "bye", "launch", "")
Segment(window, "last one", "exit", "end")

# widgets with function:
# create_segment(window, "label", "button").pack(expand=True, fill="both", pady=10, padx=10)
# create_segment(window, "test", "click").pack(expand=True, fill="both", pady=10, padx=10)
# create_segment(window, "hello", "test").pack(expand=True, fill="both", pady=10, padx=10)
# create_segment(window, "bye", "launch").pack(expand=True, fill="both", pady=10, padx=10)
# create_segment(window, "last one", "exit").pack(expand=True, fill="both", pady=10, padx=10)

'''
EX11:    
    - Crie um segmento menor dentro da classe usando uma função/método
    - Ele deve ser um container que tem um campo de Entry e um botão, empilhados com "top"
    - O texto do botão deve ser passado via parâmetro
    - Tudo devve estar na terceira coluna
'''

# run
window.mainloop()