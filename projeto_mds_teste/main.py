import customtkinter as ctk
# import tkinter as tk
from gui import MDSApp

def main():

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = MDSApp(root)
    root.geometry("800x600")
    root.mainloop()

if __name__ == "__main__":
    main()
