"""Console logging functionality for GUI applications."""

import tkinter as tk


class ConsoleLogger:
    """Handle console output logging to GUI text widget."""

    def __init__(self, console_widget: tk.Text):
        """Initialize the console logger.

        Args:
            console_widget (tk.Text): Text widget for displaying console output
        """
        self.console = console_widget

    def log(self, message):
        """Log message to the console widget.

        Args:
            message: The message to log to console
        """
        if self.console:
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, message + "\n")
            self.console.see(tk.END)
            self.console.config(state=tk.DISABLED)
