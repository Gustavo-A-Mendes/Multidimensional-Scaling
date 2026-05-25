import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback
import ctypes

# Habilitar nitidez High DPI no Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass  # Ignora em SOs diferentes ou Windows mais antigos

# Tratamento global de exceções para que o executável não feche silenciosamente
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("Fatal Error:", error_msg)
    
    # Exibe caixa de diálogo do Tkinter
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Erro Fatal Inesperado", f"Ocorreu um erro no aplicativo:\n\n{exc_value}\n\nVerifique o console ou contate o suporte.")
    root.destroy()

sys.excepthook = handle_exception

# Ajusta o sys.path para que imports absolutos como 'mds_app.ui...' funcionem corretamente
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from mds_app.ui.main_window import MainWindow

def main():
    root = tk.Tk()
    
    # Previne que o app fique aberto em segundo plano no Gerenciador de Tarefas
    def on_closing():
        try:
            import matplotlib.pyplot as plt
            plt.close('all')  # Fecha de forma limpa todas as figuras do Matplotlib e libera recursos
        except Exception:
            pass
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Tentar aplicar escala de fonte/interface pro Windows Dpi Aware
    try:
        root.tk.call('tk', 'scaling', root.winfo_fpixels('1i') / 72.0)
    except Exception:
        pass
        
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
