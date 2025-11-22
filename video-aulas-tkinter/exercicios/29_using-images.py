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

def stretch_image(event):
    global resized_tk

    width = event.width
    height = event.height
    # print(width, height)

    # create an image:
    resized_image = image_original.resize((width, height))
    resized_tk = ImageTk.PhotoImage(resized_image)

    # place on the canvas:
    canvas.create_image(0, 0, image=resized_tk, anchor=tk.NW)

def fill_image(event):
    global resized_tk
    # global image_ratio

    # current ratio:
    canvas_ratio = event.width / event.height

    # get coordinates:
    if canvas_ratio > image_ratio:
        width = event.width
        height = int(width / image_ratio)
    else:
        height = event.height
        width = int(height * image_ratio)

    resized_image = image_original.resize((width, height))
    resized_tk = ImageTk.PhotoImage(resized_image)
    canvas.create_image(
        int(event.width/2),
        int(event.height/2),
        image=resized_tk,
        anchor=tk.CENTER)

""" 
    EX19:
        - Crie um terceiro comportamento de escala para sempre mostrar a imagem inteira, sem partes recortadas
"""


def show_full_image(event):
    global resized_tk
    # global image_ratio

    # current ratio:
    canvas_ratio = event.width / event.height

    # get coordinates:
    if canvas_ratio < image_ratio:
        width = event.width
        height = int(width / image_ratio)
    else:
        height = event.height
        width = int(height * image_ratio)

    resized_image = image_original.resize((width, height))
    resized_tk = ImageTk.PhotoImage(resized_image)
    canvas.create_image(
        int(event.width/2),
        int(event.height/2),
        image=resized_tk,
        anchor=tk.CENTER)



# grid layout:
window.columnconfigure((0, 1, 2, 3), weight=1, uniform='a')

window.rowconfigure(0, weight=1)
# import an image:
image_original = Image.open('../raccoon.jpg')
image_ratio = image_original.size[0] / image_original.size[1]
print(image_ratio)

image_tk = ImageTk.PhotoImage(image_original)
python_dark = Image.open('../python_dark.png').resize((30, 30))

python_dark_tk = ImageTk.PhotoImage(python_dark)

img_ctk = ctk.CTkImage(
    light_image=Image.open('../python_dark.png').resize((30, 30)),
    dark_image=Image.open('../python_light.png').resize((30, 30)),
)
# widget:
# label = ttk.Label(window, text="raccoon", image=image_tk)
# label.pack()

button_frame = ttk.Frame(master=window)
button = ttk.Button(button_frame, text="A button", image=python_dark_tk, compound=tk.LEFT)

button.pack()
button_ctk = ctk.CTkButton(button_frame, text="A button", image=img_ctk, compound=tk.LEFT)

button_ctk.pack()

button_frame.grid(row=0, column=0, sticky=tk.NSEW)
# canvas -> image:
canvas = tk.Canvas(window, background="black", bd=0, highlightthickness=0, relief=tk.RIDGE)
canvas.grid(row=0, column=1, columnspan=3, sticky=tk.NSEW)
# canvas.create_image(0, 0, image=image_tk, anchor=tk.NW)

canvas.bind("<Configure>", fill_image)

# run:
window.mainloop()