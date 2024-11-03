import tkinter.font as tk_font
import tkinter as tk

class ToolTip:
    """A simple tooltip class for Tkinter."""
    def __init__(self, root, widget, text, theme, font, background, foreground):
        self.root = root
        self.widget = widget
        self.tooltip_text = text
        self.tooltip_bg = background
        self.tooltip_fg = foreground
        self.tooltip_font = font
        self.tooltip_theme = theme
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    @property
    def root(self): return self._root
    @root.setter
    def root(self, value): self._root = value

    @property
    def widget(self): return self._widget
    @widget.setter
    def widget(self, value): self._widget = value

    @property
    def tooltip_text(self): return self._tooltip_text
    @tooltip_text.setter
    def tooltip_text(self, value): self._tooltip_text = value

    @property
    def tooltip_bg(self): return self._tooltip_bg
    @tooltip_bg.setter
    def tooltip_bg(self, value): self._tooltip_bg = value

    @property
    def tooltip_fg(self): return self._tooltip_fg
    @tooltip_fg.setter
    def tooltip_fg(self, value): self._tooltip_fg = value
    
    def show_tooltip(self, event=None):
        if self.tooltip_window is not None:
            return  # Tooltip already visible
        temp_label = tk.Label(self.widget, text=self.tooltip_text)
        temp_label.update_idletasks()  # Update the label to get the width and height of the tooltip with current text
        tooltip_height = temp_label.winfo_reqheight() + 10
        if self.root.winfo_width() - self.widget.winfo_rootx() < 100:
            x = self.widget.winfo_rootx() - 100
        else:
            x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty()+tooltip_height + 10
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.tooltip_text, foreground=self.tooltip_fg,
                         background=self.tooltip_bg, borderwidth=1, padx=5, pady=3, relief="solid",
                         font=tk_font.Font(family=tk_font.families()[self.tooltip_font], size=10))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window is not None:
            self.tooltip_window.destroy()
            self.tooltip_window = None
