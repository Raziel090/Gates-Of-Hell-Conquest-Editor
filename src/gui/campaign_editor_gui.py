"""Campaign editor GUI main application window."""

import os
from pathlib import Path
from tkinter import ttk
from ttkthemes import ThemedTk
from src.console_logger import ConsoleLogger
from src.gui.inventory_manager_gui import InventoryManagerGUI
from src.gui.unit_manager_gui import UnitManagerGUI
from src.constants import (
    # GUI Configuration Constants
    THEME_NAME,
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    DATA_DIR_NAME,
    # Style Constants
    RED_LABEL_STYLE,
    GREEN_LABEL_STYLE,
    TFRAME_STYLE,
    # Color Constants
    RED_COLOR,
    GREEN_COLOR,
    # Style Properties
    FOREGROUND_PROPERTY,
    BACKGROUND_PROPERTY,
    # Pack Options
    PACK_FILL_BOTH,
    PACK_EXPAND_TRUE,
    # String Constants
    EMPTY_STRING,
    GEOMETRY_FORMAT,
    # Numeric Constants
    CENTER_DIVISOR,
)


class CampaignEditorGUI:
    """Main GUI application for campaign editing tools."""

    def __init__(self) -> None:
        """Initialize the campaign editor GUI."""
        self.master = ThemedTk(theme=THEME_NAME)
        self.game_install_dir = EMPTY_STRING
        self.campaign_file_path = EMPTY_STRING
        self.data_dir_path = str(Path(os.getcwd()) / DATA_DIR_NAME)

        self.console_text = None
        self.logger: ConsoleLogger = None

    def create_gui(self) -> None:
        """Create and configure the main GUI interface."""
        self.master.set_theme(THEME_NAME)
        self.master.title(WINDOW_TITLE)
        self.center_window(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.master.resizable(False, False)

        style = ttk.Style()
        # Configure a red foreground for the label initially
        style.configure(RED_LABEL_STYLE, foreground=RED_COLOR)
        style.configure(GREEN_LABEL_STYLE, foreground=GREEN_COLOR)

        bg_color = style.lookup(TFRAME_STYLE, BACKGROUND_PROPERTY)
        self.master.configure(background=bg_color)

        # Create notebook widget for tabs
        parent_notebook = ttk.Notebook(self.master)
        parent_notebook.pack(fill=PACK_FILL_BOTH, expand=True)

        self.unit_manager_gui = UnitManagerGUI(parent_notebook)
        self.unit_manager_gui.create_gui()

        self.inventory_manager_gui = InventoryManagerGUI(parent_notebook)
        self.inventory_manager_gui.create_gui()

    def run(self) -> None:
        """Run the GUI application."""
        self.create_gui()
        self.master.mainloop()

    def center_window(self, width: int, height: int) -> None:
        """Center the application window on screen.

        Args:
            width (int): Window width in pixels
            height (int): Window height in pixels
        """
        # Get screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Calculate position coordinates
        x = (screen_width - width) // CENTER_DIVISOR
        y = (screen_height - height) // CENTER_DIVISOR

        # Set the geometry
        self.master.geometry(GEOMETRY_FORMAT.format(width, height, x, y))
