import tkinter as tk
from tkinter import ttk

# ============================================================
# RESPONSIVE LAYOUT

class App(tk.Tk):
    def __init__(self, start_size):
        super().__init__()

        # setup:
        self.title("Responsive Layout")
        self.geometry(f"{start_size[0]}x{start_size[1]}")

        self.frame = ttk.Frame(self)
        self.frame.pack(expand=True, fill="both")

        # size notifier:
        SizeNotifier(self, {
            600: self.create_medium_layout,
            300: self.create_small_layout,
            1200: self.create_large_layout
        })

        # run:
        self.mainloop()

    def create_small_layout(self):
        # cleaning layout:
        self.frame.pack_forget()

        self.frame = ttk.Frame(self)
        ttk.Label(self.frame, text="Label 1", background="red").pack(expand=True, fill="both", padx=10, pady=5)
        ttk.Label(self.frame, text="Labes 2", background="green").pack(expand=True, fill="both", padx=10, pady=5)
        ttk.Label(self.frame, text="Labes 3", background="blue").pack(expand=True, fill="both", padx=10, pady=5)
        ttk.Label(self.frame, text="Labes 4", background="yellow").pack(expand=True, fill="both", padx=10, pady=5)

        self.frame.pack(expand=True, fill="both")

    def create_medium_layout(self):
        # cleaning layout:
        self.frame.pack_forget()

        self.frame = ttk.Frame(self)
        self.frame.columnconfigure((0, 1), weight=1, uniform='a')
        self.frame.rowconfigure((0, 1), weight=1, uniform='a')
        
        ttk.Label(self.frame, text="Label 1", background="red").grid(row=0, column=0, sticky="news", padx=10, pady=10)
        ttk.Label(self.frame, text="Labes 2", background="green").grid(row=0, column=1, sticky="news", padx=10, pady=10)
        ttk.Label(self.frame, text="Labes 3", background="blue").grid(row=1, column=0, sticky="news", padx=10, pady=10)
        ttk.Label(self.frame, text="Labes 4", background="yellow").grid(row=1, column=1, sticky="news", padx=10, pady=10)

        self.frame.pack(expand=True, fill="both")
        
    def create_large_layout(self):
        # cleaning layout:
        self.frame.pack_forget()

        self.frame = ttk.Frame(self)
        self.frame.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')
        self.frame.rowconfigure((0), weight=1, uniform='a')
        
        ttk.Label(self.frame, text="Label 1", background="red").grid(row=0, column=0, sticky="news", padx=10, pady=10)
        ttk.Label(self.frame, text="Labes 2", background="green").grid(row=0, column=1, sticky="news", padx=10, pady=10)
        ttk.Label(self.frame, text="Labes 3", background="blue").grid(row=0, column=2, sticky="news", padx=10, pady=10)
        ttk.Label(self.frame, text="Labes 4", background="yellow").grid(row=0, column=3, sticky="news", padx=10, pady=10)

        self.frame.pack(expand=True, fill="both")


class SizeNotifier:
    def __init__(self, window, size_dict):
        self.window = window
        self.size_dict = {key: value for key, value in sorted(size_dict.items())}
        # self.size_dict = dict(sorted(size_dict.items()))
        self.current_min_size = None
        
        # event to check window size:
        self.window.bind("<Configure>", self.check_size)
        
        self.window.update()

        min_height = self.window.winfo_height()
        min_width = list(self.size_dict)[0]

        self.window.minsize(min_width, min_height)


    def check_size(self, event):
        
        # checking if the event is from the main window:
        if event.widget == self.window:
            window_width = event.width
            checked_size = None

            for min_size in self.size_dict:
                delta = window_width - min_size
                if delta >= 0:
                    checked_size = min_size

            if checked_size != self.current_min_size:
                self.current_min_size = checked_size
                self.size_dict[self.current_min_size]()

'''
EX12:    
    - Crie um terceiro layout onde os widgets estão próximos uns dos outros
    - Faça ele aparecer quando a janela for maior que 1200 pixels
'''

app = App((400, 300))