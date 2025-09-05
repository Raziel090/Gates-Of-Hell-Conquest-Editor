import json
import os
from pathlib import Path
from tkinter import filedialog, ttk
import tkinter as tk
from src.console_logger import ConsoleLogger
from src.constants import INVENTORY_MANAGER_CACHE
from src.entity_inventory import EntityInventory
from src.managers.game_manager import GameManager

# UI Text Constants
DEFAULT_MANAGER_NAME = "Basic Manager"
SPECIFY_GAME_DIR_BUTTON = "Specify Game Directory"
SPECIFY_DATA_DIR_BUTTON = "Specify Extracted Data Directory"
LOAD_CAMPAIGN_BUTTON = "Load Campaign Save"
SAVE_CHANGES_BUTTON = "Save Changes"
RESTORE_BACKUP_BUTTON = "Restore Backup"
CAMPAIGN_NAME_LABEL = "Selected Campaign Name:"

# Status Messages
GAME_DIR_NOT_SET = "Game Installation Directory: Not Set"
CAMPAIGN_FILE_NOT_SET = "Campaign File: Not Set"
CAMPAIGN_FILE_INVALID = "Campaign File: Invalid"

# Tooltip Messages
GAME_DIR_TOOLTIP = (
    "Specify the path to game installation directory.\n"
    "It should contain folders such as 'resource', 'binaries' and 'localizations'.\n"
)
DATA_DIR_TOOLTIP = (
    "Specify the path to a directory with previously extracted data.\n"
    "It should contain folders such as 'entity', 'properties' and 'set'.\n"
)
CAMPAIGN_TOOLTIP = (
    "Load conquest save file to edit.\n"
    "It should be in documents\\my games\\gates of hell\\profiles\\numbers\\campaign or in\n"
    "<username>\\AppData\\Local\\digitalmindsoft\\gates of hell\\profiles\\<numbers>\\campaign\n"
)
PROCESS_TOOLTIP = (
    "When both Game Installation Directory and Campaign File are OK (green text)\n"
    "click to load all information.\n"
)
SAVE_TOOLTIP = (
    "When You're done with changes, click to save the campaign.\n"
    "During the save, last working copy of your save file will be stored as a backup\n"
)
RESTORE_TOOLTIP = (
    "Restore the last backup of the campaign file.\n"
    "This will overwrite the current campaign file with the backup.\n"
    "Make sure to save your changes after restoring a backup.\n"
)

# Dialog Titles
SELECT_GAME_DIR_TITLE = "Select Game Installation Directory"
SELECT_DATA_DIR_TITLE = "Select Extracted Data Directory"
SELECT_CAMPAIGN_TITLE = "Select Campaign Save File"

# File Patterns
SAVE_FILE_PATTERN = "*.sav"
SAVE_FILES_LABEL = "Save Files"

# Directory Names
DATA_DIR_NAME = "data"
RESOURCE_DIR_NAME = "resource"
ENTITY_DIR_NAME = "entity"
PROPERTIES_DIR_NAME = "properties"
SET_DIR_NAME = "set"
CAMPAIGN_DIR_NAME = "campaign"

# File Names
GAMELOGIC_PAK = "gamelogic.pak"
PROPERTIES_PAK = "properties.pak"

# Widget Configuration
TOOLTIP_BBOX_POSITION = "insert"
TOOLTIP_BACKGROUND = "white"
TOOLTIP_FONT = ("Arial", "10", "normal")
CAMPAIGN_NAME_FONT = ("Arial", 14)
CONSOLE_BG_COLOR = "#212121"
CONSOLE_FG_COLOR = "#CCCCCC"
CONSOLE_FONT = ("Consolas", 9)

# Widget Positioning
HORIZONTAL_ORIENTATION = "horizontal"
SIDE_LEFT = "left"
SIDE_RIGHT = "right"
FILL_BOTH = "both"
FILL_Y = "y"
FILL_X = "x"

# TTK Styles
RED_LABEL_STYLE = "Red.TLabel"
GREEN_LABEL_STYLE = "Green.TLabel"
TFRAME_BACKGROUND = "background"
TFRAME_STYLE = "TFrame"

# Dialog and UI Configuration
DIALOG_GEOMETRY = "300x150"
MESSAGE_WRAP_LENGTH = 260
TEXT_JUSTIFY_CENTER = "center"
BUTTON_PADX = 10
EXPAND_FALSE = False
EXPAND_TRUE = True

# Button Text
YES_BUTTON_TEXT = "Yes"
NO_BUTTON_TEXT = "No"

# Unit Types and Status
UNKNOWN_UNIT = "Unknown"
HUMAN_UNIT_TYPE = "Human"
ENTITY_UNIT_TYPE = "Entity"
EARLY_PERIOD = "early"
MID_PERIOD = "mid"
LATE_PERIOD = "late"

# Cache Dictionary Keys
GAME_INSTALL_DIR_KEY = "game_install_dir"
CAMPAIGN_FILE_PATH_KEY = "campaign_file_path"
DATA_DIR_PATH_KEY = "data_dir_path"

# File Names
CAMPAIGN_SCN_FILE = "campaign.scn"
STATUS_FILE = "status"
BACKUP_EXTENSION = ".bak"

# Unit Status Values
DECEASED_UNIT_ID = "0xffffffff"
DECEASED_UNIT_NAME = "Deceased"
NA_UNIT_TYPE = "N/A"

# Log Messages
INVALID_GAME_DIR_MSG = (
    "Invalid game installation directory selected. "
    "Please select a valid directory containing 'resource' folder."
)
MISSING_GAMELOGIC_PAK_MSG = "The 'resource' folder is missing 'gamelogic.pak' file."
MISSING_PROPERTIES_PAK_MSG = "The 'resource' folder is missing 'properties.pak' file."
MISSING_ENTITY_DIR_MSG = "The 'resource' folder is missing 'entity' directory."
INVALID_DATA_DIR_ENTITY_MSG = (
    "Invalid data directory selected. "
    "Please select a valid directory containing 'entity' folder."
)
INVALID_DATA_DIR_SET_MSG = (
    "Invalid data directory selected. "
    "Please select a valid directory containing 'set' folder."
)
INVALID_DATA_DIR_PROPERTIES_MSG = (
    "Invalid data directory selected. "
    "Please select a valid directory containing 'properties' folder."
)
SETTINGS_LOADED_MSG = "Settings loaded from cache."
SETTINGS_SAVED_MSG = "Settings saved to cache."
NO_BACKUP_CAMPAIGN_MSG = "No campaign backup file found to restore."
NO_BACKUP_STATUS_MSG = "No campaign status backup file found to restore."


class ToolTip:
    """Creates and manages a tooltip for a given Tkinter widget."""

    def __init__(self, widget: tk.Widget) -> None:
        """
        Initialize the tooltip with the target widget.

        Args:
            widget (tk.Widget): The widget to attach the tooltip to.
        """
        self.widget = widget
        self.tipwindow = None
        self.text = ""

    def showtip(self, text: str) -> None:
        """
        Display the tooltip with the provided text.

        Args:
            text (str): The text to display in the tooltip.
        """
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox(TOOLTIP_BBOX_POSITION)
        x += self.widget.winfo_rootx() + 30
        y += cy + self.widget.winfo_rooty() + 30
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify=tk.LEFT,
            background=TOOLTIP_BACKGROUND,
            relief=tk.SOLID,
            borderwidth=1,
            font=TOOLTIP_FONT,
        )
        label.pack(side=tk.BOTTOM)

    def hidetip(self) -> None:
        """Hide the tooltip if it is currently displayed."""
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class ManagerGUI:
    """Base class for Manager GUI applications."""

    def __init__(self, parent_notebook: ttk.Notebook) -> None:
        """Initialize the Manager GUI.

        Args:
            parent_notebook (ttk.Notebook): The parent notebook widget to contain tabs
        """
        self.parent_notebook = parent_notebook
        self.game_install_dir = ""
        self.campaign_file_path = ""
        self.data_dir_path = str(Path(os.getcwd()) / DATA_DIR_NAME)

        self.console_text = None
        self.logger: ConsoleLogger = None

        self.manager_name = DEFAULT_MANAGER_NAME

    def create_generic_data_management_content(self, parent_frame: ttk.Frame) -> None:
        """Create content for the generic data management section.

        Args:
            parent_frame (ttk.Frame): The parent frame to contain the management widgets
        """
        load_game_install_dir_button = ttk.Button(
            parent_frame,
            text=SPECIFY_GAME_DIR_BUTTON,
            command=self.load_game_install_dir,
        )
        load_game_install_dir_button.pack(pady=10, padx=10, fill=FILL_X)
        self.create_tooltip(
            load_game_install_dir_button,
            text=GAME_DIR_TOOLTIP,
        )

        load_data_dir_button = ttk.Button(
            parent_frame,
            text=SPECIFY_DATA_DIR_BUTTON,
            command=self.load_data_dir,
        )
        load_data_dir_button.pack(pady=10, padx=10, fill=FILL_X)
        self.create_tooltip(
            load_data_dir_button,
            text=DATA_DIR_TOOLTIP,
        )

        load_campaign_button = ttk.Button(
            parent_frame,
            text=LOAD_CAMPAIGN_BUTTON,
            command=self.load_campaign_file,
        )
        load_campaign_button.pack(pady=10, padx=10, fill=FILL_X)
        self.create_tooltip(
            load_campaign_button,
            text=CAMPAIGN_TOOLTIP,
        )

        process_button = ttk.Button(
            parent_frame,
            text=f"Process {self.manager_name}",
            command=self.prepare_manager,
        )
        process_button.pack(pady=10, padx=10, fill=FILL_X)
        self.create_tooltip(
            process_button,
            text=PROCESS_TOOLTIP,
        )

        # Add a separator
        ttk.Separator(parent_frame, orient=HORIZONTAL_ORIENTATION).pack(
            fill=FILL_X, pady=15, padx=10
        )

        # Add status label
        self.game_install_dir_status_label = ttk.Label(
            parent_frame, text=GAME_DIR_NOT_SET
        )
        self.game_install_dir_status_label.pack(pady=5, padx=10, fill=FILL_X)
        self.game_install_dir_status_label.configure(style=RED_LABEL_STYLE)

        self.campaign_file_status_label = ttk.Label(
            parent_frame, text=CAMPAIGN_FILE_NOT_SET
        )
        self.campaign_file_status_label.pack(pady=5, padx=10, fill=FILL_X)
        self.campaign_file_status_label.configure(style=RED_LABEL_STYLE)

        # Add a separator
        ttk.Separator(parent_frame, orient=HORIZONTAL_ORIENTATION).pack(
            fill=FILL_X, pady=15, padx=10
        )

        save_changes_button = ttk.Button(
            parent_frame,
            text=SAVE_CHANGES_BUTTON,
            command=self.save_changes,
        )
        save_changes_button.pack(pady=10, padx=10, fill=FILL_X)
        self.create_tooltip(
            save_changes_button,
            text=SAVE_TOOLTIP,
        )

        restore_backup_button = ttk.Button(
            parent_frame,
            text=RESTORE_BACKUP_BUTTON,
            command=self.restore_backup,
        )
        restore_backup_button.pack(pady=10, padx=10, fill=FILL_X)
        self.create_tooltip(
            restore_backup_button,
            text=RESTORE_TOOLTIP,
        )

        # Add a separator
        ttk.Separator(parent_frame, orient=HORIZONTAL_ORIENTATION).pack(
            fill=FILL_X, pady=15, padx=10
        )

        campaign_info_frame = ttk.Frame(parent_frame)
        campaign_info_frame.pack(fill=FILL_X, padx=10, pady=(5, 0), expand=EXPAND_FALSE)

        # Create variable to track campaign name
        self.campaign_name_str_var = tk.StringVar(value="")

        # Create custom font for larger text
        campaign_name_font = CAMPAIGN_NAME_FONT

        # Campaign name Display - stacked vertically
        campaign_name_description_label = ttk.Label(
            campaign_info_frame, text=CAMPAIGN_NAME_LABEL
        )
        campaign_name_description_label.pack(anchor="w", pady=(0, 2))

        campaign_name_label = ttk.Label(
            campaign_info_frame,
            textvariable=self.campaign_name_str_var,
            font=campaign_name_font,
            wraplength=200,
        )
        campaign_name_label.pack(anchor="w")

        # Add a separator
        ttk.Separator(parent_frame, orient=HORIZONTAL_ORIENTATION).pack(
            fill=FILL_X, pady=15, padx=10
        )

    def create_generic_console_frame_content(
        self, console_frame: ttk.LabelFrame
    ) -> None:
        """Create console frame content for unit manager."""
        # === CONSOLE FRAME CONTENT ===
        # Create console text widget with scrollbar
        self.console_text = tk.Text(
            console_frame,
            wrap=tk.WORD,
            width=40,
            height=25,
            bg=CONSOLE_BG_COLOR,
            fg=CONSOLE_FG_COLOR,
            font=CONSOLE_FONT,
        )
        self.console_text.pack(side=SIDE_LEFT, fill=FILL_BOTH, expand=True)

        # Add scrollbar to console
        scrollbar = ttk.Scrollbar(console_frame, command=self.console_text.yview)
        scrollbar.pack(side=SIDE_RIGHT, fill=FILL_Y)
        self.console_text.config(yscrollcommand=scrollbar.set)

        # Make console read-only
        self.console_text.config(state=tk.DISABLED)

        self.logger = ConsoleLogger(self.console_text)

    def get_selected_unit_info(
        self, game_manager: GameManager, squad_id: int, squad_member_id: str
    ) -> tuple[str, str, EntityInventory]:
        """Show selected unit info for unit manager."""
        if squad_member_id == DECEASED_UNIT_ID:
            unit_name = DECEASED_UNIT_NAME
            unit_type = NA_UNIT_TYPE
            unit_inventory = None
            return unit_name, unit_type, unit_inventory

        squad_inventories = game_manager.squads_inventories[squad_id].inventories
        unit_inventory = squad_inventories[squad_member_id]
        unit_name = unit_inventory.entity_breed if unit_inventory else UNKNOWN_UNIT
        unit_type = (
            HUMAN_UNIT_TYPE
            if any(
                substr in unit_name
                for substr in [EARLY_PERIOD, MID_PERIOD, LATE_PERIOD]
            )
            else ENTITY_UNIT_TYPE
        )

        return unit_name, unit_type, unit_inventory

    def create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """Create a tooltip for the given widget.

        Args:
            widget (tk.Widget): The widget to attach the tooltip to
            text (str): The text to display in the tooltip
        """
        tooltip = ToolTip(widget)

        def enter(event: tk.Event) -> None:
            tooltip.showtip(text)

        def leave(event: tk.Event) -> None:
            tooltip.hidetip()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def load_game_install_dir(self) -> None:
        """Load and validate game installation directory."""
        game_install_dir_path = filedialog.askdirectory(
            title=SELECT_GAME_DIR_TITLE,
            mustexist=True,
        )

        game_install_dir_path = Path(game_install_dir_path)

        correct_dir = True
        if not (game_install_dir_path / RESOURCE_DIR_NAME).exists():
            self.logger.log(INVALID_GAME_DIR_MSG)
            correct_dir = False

        if not (game_install_dir_path / RESOURCE_DIR_NAME / GAMELOGIC_PAK).exists():
            self.logger.log(MISSING_GAMELOGIC_PAK_MSG)
            correct_dir = False

        if not (game_install_dir_path / RESOURCE_DIR_NAME / PROPERTIES_PAK).exists():
            self.logger.log(MISSING_PROPERTIES_PAK_MSG)
            correct_dir = False

        if not (game_install_dir_path / RESOURCE_DIR_NAME / ENTITY_DIR_NAME).exists():
            self.logger.log(MISSING_ENTITY_DIR_MSG)
            correct_dir = False

        if not correct_dir:
            self.update_label_status(
                self.game_install_dir_status_label,
                text="Game Installation Directory: Invalid",
                style=RED_LABEL_STYLE,
            )
            return

        self.logger.log(
            f"Game installation directory selected: {game_install_dir_path}"
        )

        self.game_install_dir = str(game_install_dir_path)

        self.update_label_status(
            self.game_install_dir_status_label,
            text="Game Installation Directory: OK",
            style=GREEN_LABEL_STYLE,
        )
        # Save cache after updating
        self.save_cache()

    def load_data_dir(self) -> None:
        """Load and validate extracted data directory."""
        data_dir_path = filedialog.askdirectory(
            title=SELECT_DATA_DIR_TITLE,
            mustexist=True,
        )

        data_dir_path = Path(data_dir_path)

        correct_dir = True
        if not (data_dir_path / ENTITY_DIR_NAME).exists():
            self.logger.log(INVALID_DATA_DIR_ENTITY_MSG)
            correct_dir = False
        if not (data_dir_path / SET_DIR_NAME).exists():
            self.logger.log(INVALID_DATA_DIR_SET_MSG)
            correct_dir = False
        if not (data_dir_path / PROPERTIES_DIR_NAME).exists():
            self.logger.log(INVALID_DATA_DIR_PROPERTIES_MSG)
            correct_dir = False

        if not correct_dir:
            self.update_label_status(
                self.game_install_dir_status_label,
                text="Data Directory: Invalid",
                style=RED_LABEL_STYLE,
            )
            return

        self.logger.log(f"Data directory selected: {data_dir_path}")

        self.data_dir_path = str(data_dir_path)

        self.update_label_status(
            self.game_install_dir_status_label,
            text="Data Directory: OK",
            style=GREEN_LABEL_STYLE,
        )

        # Save cache after updating
        self.save_cache()

    def load_campaign_file(self) -> None:
        """Load and validate campaign save file."""
        campaign_file = filedialog.askopenfile(
            title=SELECT_CAMPAIGN_TITLE,
            filetypes=[(SAVE_FILES_LABEL, SAVE_FILE_PATTERN)],
        )

        if not campaign_file:
            self.update_label_status(
                self.campaign_file_status_label,
                text=CAMPAIGN_FILE_INVALID,
                style=RED_LABEL_STYLE,
            )
            return

        self.logger.log(f"Campaign file selected: {campaign_file.name}")

        self.campaign_file_path = campaign_file.name

        self.update_label_status(
            self.campaign_file_status_label,
            text="Campaign File: OK",
            style=GREEN_LABEL_STYLE,
        )

        self.campaign_name_str_var.set(os.path.basename(str(campaign_file.name)))

        # Save cache after updating
        self.save_cache()

    def update_label_status(self, label: ttk.Label, text: str, style: str) -> None:
        """Update label text and style.

        Args:
            label (ttk.Label): The label widget to update
            text (str): The new text to display
            style (str): The style to apply to the label
        """
        label.configure(style=style, text=text)

    def load_cache(self) -> dict:
        """Load cached settings from file."""
        cache_file = Path(os.getcwd()) / INVENTORY_MANAGER_CACHE
        default_cache = {
            GAME_INSTALL_DIR_KEY: "",
            CAMPAIGN_FILE_PATH_KEY: "",
            DATA_DIR_PATH_KEY: str(Path(os.getcwd()) / DATA_DIR_NAME),
        }

        if not cache_file.exists():
            return default_cache

        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
            self.logger.log(SETTINGS_LOADED_MSG)
            return cache
        except Exception as e:
            self.logger.log(f"Error loading cache: {str(e)}")
            return default_cache

    def save_cache(self) -> None:
        """Save current settings to cache file."""
        cache_file = Path(os.getcwd()) / f"{self.__class__.__name__.lower()}_cache.json"
        cache = {
            GAME_INSTALL_DIR_KEY: self.game_install_dir,
            CAMPAIGN_FILE_PATH_KEY: self.campaign_file_path,
            DATA_DIR_PATH_KEY: self.data_dir_path,
        }

        try:
            with open(cache_file, "w") as f:
                json.dump(cache, f, indent=4)
            self.logger.log(SETTINGS_SAVED_MSG)
        except Exception as e:
            self.logger.log(f"Error saving cache: {str(e)}")

    def update_ui_from_cache(self) -> None:
        """Update UI elements from cached values."""
        # Update game install dir status
        if self.game_install_dir and Path(self.game_install_dir).exists():
            self.update_label_status(
                self.game_install_dir_status_label,
                text="Game Installation Directory: OK",
                style=GREEN_LABEL_STYLE,
            )
            self.logger.log(f"Loaded game dir from cache: {self.game_install_dir}")

        # Update campaign file status
        if self.campaign_file_path and Path(self.campaign_file_path).exists():
            self.update_label_status(
                self.campaign_file_status_label,
                text="Campaign File: OK",
                style=GREEN_LABEL_STYLE,
            )
            self.logger.log(
                f"Loaded campaign file from cache: {self.campaign_file_path}"
            )

            self.campaign_name_str_var.set(os.path.basename(self.campaign_file_path))

    def prepare_manager_from_cache(self) -> None:
        if self.game_install_dir and self.campaign_file_path:
            self.prepare_manager()
            self.logger.log(f"Initialized {self.manager_name} from cache.")

    def show_confirmation_dialog(self, title: str, message: str) -> bool:
        """Show a yes/no confirmation dialog.

        Args:
            title (str): Dialog window title
            message (str): Message to display

        Returns:
            bool: True if user clicked Yes, False otherwise
        """
        dialog = tk.Toplevel(self.parent_notebook)
        dialog.title(title)
        dialog.geometry(DIALOG_GEOMETRY)
        dialog.resizable(False, False)

        # Make it modal (blocks interaction with main window)
        dialog.transient(self.parent_notebook)
        dialog.grab_set()

        # Center the dialog on the parent window
        x = (
            self.parent_notebook.winfo_x()
            + (self.parent_notebook.winfo_width() // 2)
            - 150
        )
        y = (
            self.parent_notebook.winfo_y()
            + (self.parent_notebook.winfo_height() // 2)
            - 75
        )
        dialog.geometry(f"+{x}+{y}")

        # Configure with the same theme
        style = ttk.Style(dialog)
        bg_color = style.lookup(TFRAME_STYLE, TFRAME_BACKGROUND)
        dialog.configure(background=bg_color)

        # Create a response variable
        result = tk.BooleanVar(value=False)

        # Add message
        message_label = ttk.Label(
            dialog,
            text=message,
            wraplength=MESSAGE_WRAP_LENGTH,
            justify=TEXT_JUSTIFY_CENTER,
        )
        message_label.pack(pady=(20, 10), padx=20)

        # Add buttons frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)

        # Yes button
        yes_button = ttk.Button(
            button_frame,
            text=YES_BUTTON_TEXT,
            command=lambda: [result.set(True), dialog.destroy()],
        )
        yes_button.pack(side=SIDE_LEFT, padx=BUTTON_PADX)

        # No button
        no_button = ttk.Button(
            button_frame,
            text=NO_BUTTON_TEXT,
            command=lambda: [result.set(False), dialog.destroy()],
        )
        no_button.pack(side=SIDE_LEFT, padx=BUTTON_PADX)

        # Set focus to the dialog and wait for it to close
        dialog.focus_set()
        self.parent_notebook.wait_window(dialog)

        return result.get()

    def restore_backup(self) -> None:
        """Restore the last backup of the campaign file."""
        campaign_data_file_path = (
            Path(self.data_dir_path) / CAMPAIGN_DIR_NAME / CAMPAIGN_SCN_FILE
        )
        campaign_backup_file_path = campaign_data_file_path.with_suffix(
            BACKUP_EXTENSION
        )

        campaign_status_file_path = (
            Path(self.data_dir_path) / CAMPAIGN_DIR_NAME / STATUS_FILE
        )
        campaign_status_backup_file_path = campaign_status_file_path.with_suffix(
            BACKUP_EXTENSION
        )

        if not campaign_backup_file_path.exists():
            self.logger.log(NO_BACKUP_CAMPAIGN_MSG)
            return

        if not campaign_status_backup_file_path.exists():
            self.logger.log(NO_BACKUP_STATUS_MSG)
            return

        confirm = self.show_confirmation_dialog(
            title="Restore Backup",
            message="Are you sure you want to restore the last backup?\n",
        )

        if not confirm:
            self.logger.log("Backup restore cancelled.")
            return

        try:
            with open(campaign_backup_file_path, "r") as backup_file:
                content = backup_file.read()

            with open(campaign_data_file_path, "w") as original_file:
                original_file.write(content)

            with open(campaign_status_backup_file_path, "r") as backup_file:
                content = backup_file.read()

            with open(campaign_status_file_path, "w") as original_file:
                original_file.write(content)

            self.logger.log("Backup restored successfully.")
        except Exception as e:
            self.logger.log(f"Error restoring backup: {str(e)}")

    # Abstract methods - to be overridden by child classes
    def create_gui(self) -> None:
        """Create the basic GUI structure. Override in child classes."""
        pass

    def prepare_manager(self) -> None:
        """Prepare the manager instance. Override in child classes."""
        pass

    def populate_gui_elements_with_data(self) -> None:
        """Populate GUI elements with data. Override in child classes."""
        pass

    def save_changes(self) -> None:
        """Save changes to the campaign file. Override in child classes."""
        pass
