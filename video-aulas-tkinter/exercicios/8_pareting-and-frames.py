import tkinter as tk
from tkinter import ttk

# ============================================================
# PARENTING and FRAMES

window = tk.Tk()
window.geometry('600x400')
window.title('Frames and parenting')

frame = ttk.Frame(
    window,
    width=200, 
    height=200,
    borderwidth=10,
    relief=tk.GROOVE
)
frame.pack_propagate(False)
frame.pack(side='left')

# master setting:
label = ttk.Label(
    frame, 
    text='Label in frame'
)
label.pack()

button = ttk.Button(
    frame,
    text='button in a frame'
)
button.pack()

# example:
label2 = ttk.Label(
    window,
    text='Label outside frame'
)
label2.pack(side='left')

'''
EX6:    
    - Crie um outro frame com uma label, um botão e uma Entry 
      e coloque à direita dos outros widgets
'''

frame2 = ttk.Frame(
    window,
    width=100,
    height=200,
    borderwidth=10,
    relief=tk.GROOVE
)
frame2.pack_propagate(False)

ttk.Label(frame2, text='label in frame 2').pack() 
ttk.Button(frame2, text='button in frame 2').pack()
ttk.Entry(frame2).pack()
frame2.pack(side='right')

# run:
window.mainloop()