import tkinter as tk
from tkinter import ttk

# ============================================================
# EVENT BINDING

window = tk.Tk()
window.title('Event Binding')

def get_pos(event):
    print(f'x: {event.x} y: {event.y}')

# widgets
text = tk.Text(window)
text.pack()

entry = ttk.Entry(window)
entry.pack()

button = ttk.Button(window, text='A button')
button.pack()

# events:
# => <modifier-type-detail>
# Ex. <Alt-KeyPress-A>
# Ex. <Alt-KeyPress-A>
button.bind('<Alt-KeyPress-a>', lambda event: print(event))
window.bind('<Motion>', get_pos)

window.bind('<KeyPress>', lambda event: print(f'a key was pressed ({event.char})'))

entry.bind('<FocusIn>', lambda event: print('entry field was seleced'))
entry.bind('<FocusOut>', lambda event: print('entry field was unseleced'))

'''
EX3:    
    - Imprima o 'Mousewhell' quando o usuário segurar SHIFT e usar a roda do mouse enquanto o campo "text" está selecionado
'''
text.bind('<Shift-MouseWheel>', lambda event: print('Mousewheel'))

# run
window.mainloop()