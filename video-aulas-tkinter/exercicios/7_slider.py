import tkinter as tk
from tkinter import ttk

# ============================================================
# SLIDERS

window = tk.Tk()
window.title('Sliders')

# slider: -> default scale is 0 to 1
scale_float = tk.DoubleVar(value=15)
slider = ttk.Scale(
    window,
    command=lambda value: progress.stop(),
    from_=0,
    to=25,
    length=300,
    orient='vertical',
    variable=scale_float
)
slider.pack()

# progress bar:
progress = ttk.Progressbar(
    window,
    variable=scale_float,
    maximum=25,
    orient='horizontal',
    mode='indeterminate',
    length=400
)
progress.pack()

# special methods:
# .start(delay) -> barra de progresso move sozinha
# 500 -> tempo de delay da atualização da barra
progress.start(500)
# progress.stop()

# Scrolledtext:
from tkinter import scrolledtext

scrolled_text = scrolledtext.ScrolledText(
    window,
    width=100,
    height=20
)
scrolled_text.pack()

'''
EX5:    
    - Crie uma progress bar que é vertical
    - Inicia automaticamente
    - Mostra o progresso como um número
    - Deve haver um slider que é afetado pela progress bar
'''
progress_int = tk.IntVar(value=0)
progress = ttk.Progressbar(
    window,
    maximum=100,
    variable=progress_int,
    orient='vertical'
)
progress.pack()
progress.start()

progress_label = ttk.Label(
    window,
    text='',
    textvariable=progress_int
)
progress_label.pack()


slider = ttk.Scale(
    window,
    from_=0,
    to=100,
    variable=progress_int
)
slider.pack()

# run:
window.mainloop()