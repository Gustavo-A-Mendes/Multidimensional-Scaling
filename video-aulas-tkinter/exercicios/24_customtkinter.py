import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# ============================================================
# CUSTOMTKINTER

# window:
window = ctk.CTk()
window.title("customtkinter app")
window.geometry("600x400")

def change_color():
    print("mudando a cor")
    if ctk.get_appearance_mode() == 'Dark':
        ctk.set_appearance_mode('Light')
    elif ctk.get_appearance_mode() == 'Light':
        ctk.set_appearance_mode('Dark')

# widgets:
string_var = tk.StringVar(value="a custom string")
string_var = ctk.StringVar(value="a custom string")

label = ctk.CTkLabel(
    window,
    text="A ctk label",
    fg_color=("blue","red"),
    text_color="white",
    corner_radius=10,
    textvariable=string_var
)
label.pack()

button = ctk.CTkButton(
    window,
    text="A ctk button",
    fg_color="#FF0",
    text_color="#000",
    hover_color="#AA0",
    command=change_color
)
button.pack()

frame = ctk.CTkFrame(
    window
    # fg_color="transparent"
)
frame.pack()

slider = ctk.CTkSlider(
    frame
)
slider.pack(padx=20, pady=20)

""" 
    EX17:
        - Crie um switch com o customtkinter, tal qual o apresentado:
"""

switch = ctk.CTkSwitch(
    window,
    text="Exercise Switch",
    border_color="red",
    fg_color=("blue", "red"),
    progress_color="pink",
    button_color="green",
    button_hover_color="yellow",
    switch_width=60,
    switch_height=30,
    corner_radius=2
)
switch.pack()

# run:
window.mainloop()