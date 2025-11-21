import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from PIL import Image, ImageTk

# ============================================================
# USING IMAGES IN TKINTER

# setup:
window = tk.Tk()
window.title("Images")
window.geometry("600x400")

# import an image:
image_original = Image.open('../raccoon.jpg')

label = ttk.Label(window, text="raccoon", image=image_original)
label.pack()


# run:
window.mainloop()