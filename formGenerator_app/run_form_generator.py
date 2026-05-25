import sys
import os
import tkinter as tk
from tkinter import messagebox
import traceback
import ctypes

# Adiciona o diretório pai (raiz do repositório) ao sys.path para garantir importações corretas
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Habilitar nitidez High DPI no Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Tratamento global de exceções para que o executável não feche silenciosamente
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print("Fatal Error:", error_msg)
    
    # Exibe caixa de diálogo amigável com o erro
    messagebox.showerror(
        "Erro Crítico",
        f"Ocorreu um erro inesperado e o aplicativo precisará ser fechado.\n\nDetalhes do erro:\n{error_msg}"
    )

# Sobrescreve o gancho de exceção do sistema
sys.excepthook = handle_exception

from formGenerator_app.app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = MainWindow()
    app.run()
