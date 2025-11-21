import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledFrame
from ttkbootstrap.widgets.toast import ToastNotification
from ttkbootstrap.widgets.tooltip import ToolTip
from ttkbootstrap.widgets import DateEntry, Floodgauge, Meter

# ============================================================
# CALENDAR, SCROLLBAR, TOOLTIP AND A TOAST

# window:
window = ttk.Window(themename="darkly")
window.title("extra widgets")
# window.geometry("400x300")

# scrollable frame:
scroll_frame = ScrolledFrame(window)
scroll_frame.pack(expand=True, fill="both")

for i in range(100):
    frame = ttk.Frame(scroll_frame)
    ttk.Label(frame, text=f"Label:{i}").pack(fill="x", side="left")
    ttk.Button(frame, text=f"Button:{i}").pack(fill="x", side="left")
    frame.pack(expand=True, fill="x")

# toast:
toast = ToastNotification(
    title="This is a message title",
    message="This is the actual message",
    duration=2000,
    bootstyle="warning",
    position=(50, 100, "ne")
)

# toast.show_toast()
ttk.Button(
    window,
    text="show toast",
    command=toast.show_toast
).pack(pady=10)

# tooltip:
button = ttk.Button(window, text="tooltip button", bootstyle="warning")
button.pack(pady=10)

ToolTip(button, text="This does something", bootstyle="danger-inverse")

# calendar:;
calendar = DateEntry(window, dateformat="%d/%m/%Y")
calendar.pack(pady=10)
calendar.pack(pady=10)

ttk.Button(window, text="get calendar date", command=lambda: print(calendar.entry.get())).pack()

# progress -> floodgauge:
progress_int = tk.IntVar(value=50)
progress = ttk.Floodgauge(
    window,
    text="progress",
    variable=progress_int,
    bootstyle="danger",
    mask="mask {}%"
)
progress.pack(pady=10, fill="x")
ttk.Scale(window, from_=0, to=100, variable=progress_int).pack(pady=10)

# meter:
meter = ttk.Meter(
    window,
    amounttotal=100,
    amountused=10,
    interactive=True,
    metertype="semi",
    subtext="some other text",
    bootstyle="danger",
)
meter.pack(pady=10)

# run:
window.mainloop()