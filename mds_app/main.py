import tkinter as tk
import os
from mds_app.ui.main_window import MainWindow

def main():
    root = tk.Tk()
    
    # Previne processos zumbis
    def on_closing():
        root.destroy()
        os._exit(0)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
