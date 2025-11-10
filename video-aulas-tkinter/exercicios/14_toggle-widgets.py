import tkinter as tk
from tkinter import ttk

# ============================================================
# TOGGLE WIDGETS

window = tk.Tk()
window.geometry("600x400")
window.title("Hide widgets")

# # place:
# def toggle_label_place():
#     global label_visible

#     if label_visible:
#         label_visible = False
#         label.place_forget()
#     else:
#         label_visible = True
#         label.place(relx=0.5, rely=0.5, anchor="center")

# button = ttk.Button(window, text="toggle Label", command=toggle_label_place)
# button.place(x=10, y=10)

# label_visible = True
# label = ttk.Label(window, text="A Label")
# label.place(relx=0.5, rely=0.5, anchor="center")

# grid:
def toggle_label_grid():
    global label_visible

    if label_visible:
        label_visible = False
        label.grid_forget()
    else:
        label_visible = True
        label.grid(row=0, column=1)


window.columnconfigure((0, 1), weight=1, uniform='a')
window.rowconfigure(0, weight=1, uniform='a')

button = ttk.Button(window, text="toggle Label", command=toggle_label_grid)
button.grid(row=0, column=0)

label_visible = True
label = ttk.Label(window, text="A Label")
label.grid(row=0, column=1)


# # pack:
# def toggle_label_pack():
#     global label_visible

#     if label_visible:
#         label_visible = False
#         label.pack_forget()
#         frame.pack(expand=True, before=button)
#     else:
#         label_visible = True
#         label.pack(side="top", expand=True, before=button)
#         frame.pack_forget()


# label_visible = True
# label = ttk.Label(window, text="A Label")
# label.pack(expand=True)

# frame = ttk.Frame(window)

# button = ttk.Button(window, text="toggle Label", command=toggle_label_pack)
# button.pack()

# run:
window.mainloop()