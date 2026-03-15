import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    '''
        A Custom Scrollable Widget, consisting of a Canvas with a content frame inside
        and a ScrollBar
    '''

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent)
        # ----------------------------------------------------------------------
        # creating widgets:
        # ----------------------------------------------------------------------

        # canva:
        self.canvas = tk.Canvas(self, highlightthickness=0)

        # scrollbar
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        # content frame:
        self.content = ttk.Frame(self.canvas)

        # ----------------------------------------------------------------------
        # setting widgets:
        # ----------------------------------------------------------------------

        # grid config:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # create canvas window:
        self.window_id = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # ----------------------------------------------------------------------
        # event binding:
        # ----------------------------------------------------------------------

        # scroll and mouse binding:
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)

        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # ----------------------------------------------------------------------
        # setting layout:
        # ----------------------------------------------------------------------
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

    # update scrollbar when window size changes (content frame):
    def _on_content_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        if self.content.winfo_reqheight() > self.canvas.winfo_height():
            if not self.scrollbar.winfo_manager():
                self.scrollbar.grid(row=0, column=1, sticky="ns")

        else:
            self.scrollbar.grid_forget()

    # update scrollbar when window size changes (canvas):
    def _on_canvas_configure(self, event: tk.Event) -> None:
        self.canvas.itemconfigure(self.window_id, width=event.width)

        if self.content.winfo_reqheight() > self.canvas.winfo_height():
            if not self.scrollbar.winfo_manager():
                self.scrollbar.grid(row=0, column=1, sticky="ns")

        else:
            self.scrollbar.grid_forget()

    # create mouse binding when canvas is in focus:
    def _bind_mousewheel(self, event: tk.Event) -> None:
        if self.content.winfo_height() > self.winfo_height():
            self.content.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(-int(event.delta / 120), "units"))

    # delete mouse binding when canvas isn't in focus:
    def _unbind_mousewheel(self, event: tk.Event) -> None:
        self.content.unbind_all("<MouseWheel>")

    # used to update the scrollbar when widget changes:
    def refresh(self) -> None:
        self.content.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))