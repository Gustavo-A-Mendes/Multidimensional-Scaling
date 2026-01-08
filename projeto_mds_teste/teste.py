import tkinter as tk
from sys import set_asyncgen_hooks
from tkinter import ttk
import customtkinter as ctk

root = tk.Tk()
root.title("App com Menu Lateral")
root.geometry("900x600")

# ============================================
# CRIAÇÃO DO PANEDWINDOW (divisor de áreas)
# ============================================
paned = tk.PanedWindow(root, orient="horizontal")
paned.pack(fill="both", expand=True)
paned.configure(sashrelief="ridge")

# ============================================
# MENU LATERAL (ESQUERDA)
# ============================================
frame_menu = ttk.Frame(paned, width=250)  # tamanho inicial
frame_menu.pack(fill="y", expand=False)

ttk.Label(frame_menu, text="MENU LATERAL").pack()

# Adicione seus widgets
ttk.Button(frame_menu, text="Opção 1").pack(pady=5)
ttk.Button(frame_menu, text="Opção 2").pack(pady=5)

# ============================================
# ÁREA DE VISUALIZAÇÃO (DIREITA)
# ============================================
frame_view = ttk.Frame(paned)
frame_view.pack(fill="both", expand=True)

ttk.Label(frame_view, text="ÁREA DE VISUALIZAÇÃO").pack()

# ============================================
# ADICIONAR FRAMES AO PANEDWINDOW
# ============================================
# 'weight' define se pode expandir (0 = não, 1 = pode)
paned.add(frame_menu)  # menu não deve expandir
paned.add(frame_view)  # área de visualização expande

paned.paneconfig(frame_menu, minsize=100)


root.mainloop()
