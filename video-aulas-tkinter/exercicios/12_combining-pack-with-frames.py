import tkinter as tk
from tkinter import ttk

# ============================================================
# COMBINING PACK WITH FRAMES

window = tk.Tk()
window.geometry("400x600")
window.title("Pack parenting")

# Top frame:
top_frame = ttk.Frame(window)
label1 = ttk.Label(top_frame, text="First label", background="red")
label2 = ttk.Label(top_frame, text="Label 2", background="blue")

# middle widget:
label3 = ttk.Label(window, text="Another label", background="green")

# bottom frame:
bottom_frame = ttk.Frame(window)
label4 = ttk.Label(bottom_frame, text="Last of the labels", background="orange")
button1 = ttk.Button(bottom_frame, text="A Button")
button2 = ttk.Button(bottom_frame, text="Another Button")

# top layout:
label1.pack(side="left", fill="both", expand=True)
label2.pack(side="left", fill="both", expand=True)
top_frame.pack(fill="both", expand=True)

# middle layout:
label3.pack(expand=True)

# bottom layout:
button1.pack(side="left", expand=True, fill="both")
label4.pack(side="left", expand=True, fill="both")
button2.pack(side="left", expand=True, fill="both")
bottom_frame.pack(fill="both", expand=True, padx=20, pady=20)

'''
EX9:    
    - Adicione mais 3 botões e outro Frame
    - O Frame deve estar dentro do bottom frame
    - e os botões devem estar empilhados verticalmente dentro dele
'''

# inner_bottom frame:
inner_bottom_frame = ttk.Frame(bottom_frame)
button3 = ttk.Button(inner_bottom_frame, text="Exercise button 1")
button4 = ttk.Button(inner_bottom_frame, text="Exercise button 2")
button5 = ttk.Button(inner_bottom_frame, text="Exercise button 3")

# inner layout:
button3.pack(side="top", expand=True, fill="both")
button4.pack(side="top", expand=True, fill="both")
button5.pack(side="top", expand=True, fill="both")
inner_bottom_frame.pack(side="left", expand=True, fill="both")

# run:
window.mainloop()