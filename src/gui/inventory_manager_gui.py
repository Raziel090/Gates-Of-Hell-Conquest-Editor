"""Inventory Manager GUI module for managing unit inventories and resupply operations."""

from tkinter import ttk
import tkinter as tk
from src.managers.game_manager import GameManager
from src.managers.inventory_manager import InventoryManager
from src.gui.manager_gui import ManagerGUI
from src.constants import (
    # UI Text Constants
    INVENTORY_MANAGER_TITLE,
    CONTROLS_FRAME_TITLE,
    SELECTION_FRAME_TITLE,
    CONSOLE_OUTPUT_TITLE,
    ACTIONS_FRAME_TITLE,
    # Button Text
    RESUPPLY_UNIT_BUTTON,
    RESUPPLY_SQUAD_BUTTON,
    RESUPPLY_ALL_BUTTON,
    ADD_MISSING_MEMBERS_BUTTON,
    # Label Text
    SELECT_SQUAD_LABEL,
    SELECT_SQUAD_MEMBER_LABEL,
    UNIT_TYPE_LABEL,
    UNIT_NAME_LABEL,
    UNKNOWN_LABEL,
    UNIT_INVENTORY_LABEL_TEXT,
    # Resource Display
    MP_ICON_TEXT,
    AP_ICON_TEXT,
    MP_LABEL_STYLE,
    AP_LABEL_STYLE,
    # Cache Keys
    GAME_INSTALL_DIR_KEY,
    CAMPAIGN_FILE_PATH_KEY,
    DATA_DIR_PATH_KEY,
    # Widget Configuration
    READONLY_STATE,
    COMBOBOX_WIDTH,
)

TEXT_WIDGET_WIDTH = 30
TEXT_WIDGET_HEIGHT = 5
COMBOBOX_VALUES_KEY = "value"

# Widget Dimensions and Spacing
PADX_SMALL = 5
PADX_MEDIUM = 10
PADX_LARGE = 20
PADY_SMALL = 5
PADY_MEDIUM = 10
GRID_ROW_0 = 0
GRID_ROW_1 = 1
GRID_COLUMN_0 = 0
GRID_COLUMN_1 = 1

# Widget Positioning
SIDE_LEFT = "left"
SIDE_RIGHT = "right"
SIDE_TOP = "top"
SIDE_BOTTOM = "bottom"
FILL_BOTH = "both"
FILL_X = "x"
FILL_Y = "y"
EXPAND_TRUE = True
EXPAND_FALSE = False
ANCHOR_WEST = "w"
ANCHOR_W = "w"
STICKY_WEST = "w"

# Fonts
RESOURCE_FONT = ("Arial", 14, "bold")
INVENTORY_TEXT_FONT = ("Consolas", 9)

# Colors
MP_COLOR_LOW = "red"
MP_COLOR_MEDIUM = "orange"
MP_COLOR_HIGH = "green"
AP_COLOR_LOW = "red"
AP_COLOR_MEDIUM = "orange"
AP_COLOR_HIGH = "green"
INVENTORY_TEXT_BG_COLOR = "#2a2a2a"
INVENTORY_TEXT_FG_COLOR = "#cccccc"

# Resource Thresholds
MP_LOW_THRESHOLD = 200
AP_LOW_THRESHOLD = 50
DEFAULT_RESOURCE_VALUE = 0.0
RESOURCE_DECIMAL_PRECISION = 2

# Dialog Text
SAVE_CHANGES_TITLE = "Save Changes"

# Status Messages
INVENTORY_MANAGER_STARTED_MSG = "Inventory Manager started!"
INVENTORY_MANAGER_INITIALIZED_MSG = "Inventory Manager initialized successfully."
NO_SQUADS_AVAILABLE_MSG = "No squads available to display"
NO_MEMBERS_AVAILABLE_MSG = "No squad members available"
NO_SQUAD_MEMBERS_MSG = "No squad members to resupply."
NO_SQUAD_MEMBERS_TO_ADD_MSG = "No squad members to add."
NO_SQUADS_TO_RESUPPLY_MSG = "No squads to resupply."
RESUPPLY_COMPLETED_MSG = "Resupply operation completed successfully"
NO_UNIT_SELECTED_MSG = "No unit selected for resupply"
SAVE_CANCELLED_MSG = "Save operation cancelled."
CHANGES_SAVED_MSG = "Changes saved successfully."
NO_MANAGER_INITIALIZED_MSG = "No inventory manager initialized. Cannot save changes."
SPECIFY_DIRECTORIES_MSG = (
    "Please specify Game Installation Directory or Data Directory and Campaign File."
)
SELECT_SQUAD_MEMBER_MSG = "Please select a squad member to resupply."
SAVE_CHANGES_CONFIRMATION_MSG = "Are you sure you want to save these changes to the campaign file?\n\nThis will overwrite the existing file."
ERROR_SAVING_CHANGES_MSG = "Error saving changes:"

# Tkinter Constants
TK_DISABLED = "disabled"
TK_NORMAL = "normal"
TK_WORD_WRAP = "word"
TK_END = "end"
TEXT_START_INDEX = "1.0"

# Event Binding Constants
COMBOBOX_SELECTED_EVENT = "<<ComboboxSelected>>"

# Tooltip Text
RESUPPLY_UNIT_TOOLTIP = "Resupply currently selected unit (squad member).\n"
RESUPPLY_SQUAD_TOOLTIP = "Resupply all units in the currently selected squad.\n"
RESUPPLY_ALL_TOOLTIP = "Resupply all units in all squads.\n"
ADD_MISSING_MEMBERS_TOOLTIP = (
    "Add missing squad members to the currently selected squad.\n"
)


class InventoryManagerGUI(ManagerGUI):
    """Inventory Manager GUI class for handling inventory operations and resupply management.

    Provides interface for managing unit inventories, resupplying squads, and resource management.
    """

    def __init__(self, parent_notebook: ttk.Notebook) -> None:
        """Initialize the Inventory Manager GUI.

        Args:
            parent_notebook (ttk.Notebook): The parent notebook widget to contain tabs
        """
        super().__init__(parent_notebook=parent_notebook)

        self.manager_name = INVENTORY_MANAGER_TITLE

    def create_gui(self) -> None:
        """Create the Inventory Manager GUI interface."""
        # Create inventory manager tab
        inventory_manager_tab = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(inventory_manager_tab, text=INVENTORY_MANAGER_TITLE)

        self.create_inventory_manager_tab_content(inventory_manager_tab)

    def create_inventory_manager_tab_content(self, tab_frame: ttk.Frame) -> None:
        """Create content for the inventory manager tab.

        Args:
            tab_frame (ttk.Frame): The tab frame to contain the content
        """
        # Create parent frame to hold all three panels
        parent_frame = ttk.Frame(tab_frame)
        parent_frame.pack(fill=FILL_BOTH, expand=EXPAND_TRUE)

        # Create left frame for buttons and labels
        left_frame = ttk.LabelFrame(parent_frame, text=CONTROLS_FRAME_TITLE)
        left_frame.pack(
            side=SIDE_LEFT,
            fill=FILL_BOTH,
            expand=EXPAND_TRUE,
            padx=PADX_SMALL,
            pady=PADY_MEDIUM,
        )

        # Create middle frame for comboboxes and interactive elements
        middle_frame = ttk.LabelFrame(
            parent_frame,
            text=SELECTION_FRAME_TITLE,
            width=220,
            height=400,
        )
        middle_frame.pack(
            side=SIDE_LEFT,
            fill=FILL_BOTH,
            expand=EXPAND_TRUE,
            padx=PADX_SMALL,
            pady=PADY_MEDIUM,
        )
        middle_frame.pack_propagate(False)

        # Create console frame (right side)
        console_frame = ttk.LabelFrame(parent_frame, text=CONSOLE_OUTPUT_TITLE)
        console_frame.pack(
            side=SIDE_LEFT,
            fill=FILL_BOTH,
            expand=EXPAND_TRUE,
            padx=PADX_SMALL,
            pady=PADY_MEDIUM,
        )

        self.create_inventory_manager_left_frame_content(left_frame)
        self.create_inventory_manager_middle_frame_content(middle_frame)
        self.create_inventory_manager_console_frame_content(console_frame)

        # Write initial message to console
        self.logger.log(INVENTORY_MANAGER_STARTED_MSG)

        # Load cache after logger is initialized
        cached_settings = self.load_cache()
        self.game_install_dir = cached_settings.get(GAME_INSTALL_DIR_KEY, "")
        self.campaign_file_path = cached_settings.get(CAMPAIGN_FILE_PATH_KEY, "")
        self.data_dir_path = cached_settings.get(DATA_DIR_PATH_KEY, self.data_dir_path)

        # Update UI with cached values
        self.update_ui_from_cache()

        # Prepare the manager with cached values if possible
        self.prepare_manager_from_cache()

    def create_inventory_manager_left_frame_content(
        self, left_frame: ttk.LabelFrame
    ) -> None:
        """Create content for the left control frame.

        Args:
            left_frame (ttk.LabelFrame): The left frame to contain controls
        """
        self.create_generic_data_management_content(left_frame)

        resource_frame = ttk.Frame(left_frame)
        resource_frame.pack(fill=FILL_X, padx=PADX_MEDIUM, pady=(PADY_SMALL, 0))

        # Create variables to track resource values
        self.mp_resource = tk.DoubleVar(value=DEFAULT_RESOURCE_VALUE)
        self.ap_resource = tk.DoubleVar(value=DEFAULT_RESOURCE_VALUE)

        # Create custom font for larger text
        resource_font = RESOURCE_FONT

        # MP Display
        mp_frame = ttk.Frame(resource_frame)
        mp_frame.pack(side=SIDE_LEFT, padx=(0, PADX_LARGE))

        mp_icon = ttk.Label(mp_frame, text=MP_ICON_TEXT)  # People icon or use an image
        mp_icon.pack(side=SIDE_LEFT)

        mp_label = ttk.Label(
            mp_frame, textvariable=self.mp_resource, font=resource_font
        )
        mp_label.pack(side=SIDE_LEFT, padx=(PADX_SMALL, 0))

        # AP Display
        ap_frame = ttk.Frame(resource_frame)
        ap_frame.pack(side=SIDE_LEFT)

        ap_icon = ttk.Label(
            ap_frame, text=AP_ICON_TEXT
        )  # Lightning icon or use an image
        ap_icon.pack(side=SIDE_LEFT)

        ap_label = ttk.Label(
            ap_frame, textvariable=self.ap_resource, font=resource_font
        )
        ap_label.pack(side=SIDE_LEFT, padx=(PADX_SMALL, 0))

    def create_inventory_manager_middle_frame_content(
        self, middle_frame: ttk.LabelFrame
    ) -> None:
        """Create content for the middle selection frame.

        Args:
            middle_frame (ttk.LabelFrame): The middle frame to contain selection widgets
        """
        # Squad selection
        ttk.Label(middle_frame, text=SELECT_SQUAD_LABEL).pack(
            pady=PADY_SMALL, padx=PADX_MEDIUM, anchor=ANCHOR_W
        )
        self.squad_combo = ttk.Combobox(
            middle_frame, state=READONLY_STATE, width=COMBOBOX_WIDTH
        )
        self.squad_combo.pack(pady=PADY_SMALL, padx=PADX_MEDIUM, fill=FILL_X)
        self.squad_combo.bind(COMBOBOX_SELECTED_EVENT, self.squad_selected)

        # Member selection
        ttk.Label(middle_frame, text=SELECT_SQUAD_MEMBER_LABEL).pack(
            pady=PADY_SMALL, padx=PADX_MEDIUM, anchor=ANCHOR_W
        )
        self.squad_member_combo = ttk.Combobox(
            middle_frame, state=READONLY_STATE, width=COMBOBOX_WIDTH
        )
        self.squad_member_combo.pack(pady=PADY_SMALL, padx=PADX_MEDIUM, fill=FILL_X)
        self.squad_member_combo.bind(COMBOBOX_SELECTED_EVENT, self.unit_selected)

        # Create a unit info container frame
        unit_info_frame = ttk.Frame(middle_frame)
        unit_info_frame.pack(fill=FILL_X, padx=PADX_MEDIUM, pady=PADY_SMALL)

        # Unit type and name labels
        ttk.Label(unit_info_frame, text=UNIT_TYPE_LABEL).grid(
            row=GRID_ROW_0, column=GRID_COLUMN_0, sticky=STICKY_WEST
        )
        self.unit_type_label = ttk.Label(unit_info_frame, text=UNKNOWN_LABEL)
        self.unit_type_label.grid(
            row=GRID_ROW_0,
            column=GRID_COLUMN_1,
            sticky=STICKY_WEST,
            padx=(PADX_LARGE, 0),
        )

        ttk.Label(unit_info_frame, text=UNIT_NAME_LABEL).grid(
            row=GRID_ROW_1, column=GRID_COLUMN_0, sticky=STICKY_WEST
        )
        self.unit_name_label = ttk.Label(unit_info_frame, text=UNKNOWN_LABEL)
        self.unit_name_label.grid(
            row=GRID_ROW_1,
            column=GRID_COLUMN_1,
            sticky=STICKY_WEST,
            padx=(PADX_LARGE, 0),
        )

        # Add a label for the multi-line text
        ttk.Label(middle_frame, text=UNIT_INVENTORY_LABEL_TEXT).pack(
            pady=(PADY_SMALL, 0), padx=PADX_MEDIUM, anchor=ANCHOR_W
        )

        # Create a frame to contain the text widget
        text_frame = ttk.Frame(middle_frame)
        text_frame.pack(
            fill=FILL_BOTH, expand=EXPAND_TRUE, padx=PADX_MEDIUM, pady=PADY_SMALL
        )

        # Add a multi-line text widget with scrollbar
        self.unit_inventory_text = tk.Text(
            text_frame,
            wrap=TK_WORD_WRAP,
            width=TEXT_WIDGET_WIDTH,
            height=TEXT_WIDGET_HEIGHT,  # Adjust height as needed
            bg=INVENTORY_TEXT_BG_COLOR,
            fg=INVENTORY_TEXT_FG_COLOR,
            font=INVENTORY_TEXT_FONT,
        )
        self.unit_inventory_text.pack(
            side=SIDE_LEFT, fill=FILL_BOTH, expand=EXPAND_TRUE
        )

        # Make it read-only
        self.unit_inventory_text.config(state=TK_DISABLED)

        # Add scrollbar
        details_scrollbar = ttk.Scrollbar(
            text_frame, command=self.unit_inventory_text.yview
        )
        details_scrollbar.pack(side=SIDE_RIGHT, fill=FILL_Y)
        self.unit_inventory_text.config(yscrollcommand=details_scrollbar.set)

        # Inventory actions frame
        actions_frame = ttk.LabelFrame(middle_frame, text=ACTIONS_FRAME_TITLE)
        actions_frame.pack(pady=PADY_MEDIUM, padx=PADX_MEDIUM, fill=FILL_X)

        # Action buttons
        resupply_squad_member_button = ttk.Button(
            actions_frame,
            text=RESUPPLY_UNIT_BUTTON,
            command=self.resupply_squad_member,
        )
        resupply_squad_member_button.pack(pady=PADY_SMALL, padx=PADX_SMALL, fill=FILL_X)
        self.create_tooltip(
            resupply_squad_member_button,
            text=(RESUPPLY_UNIT_TOOLTIP),
        )

        resupply_squad_button = ttk.Button(
            actions_frame, text=RESUPPLY_SQUAD_BUTTON, command=self.resupply_squad
        )
        resupply_squad_button.pack(pady=PADY_SMALL, padx=PADX_SMALL, fill=FILL_X)
        self.create_tooltip(
            resupply_squad_button,
            text=(RESUPPLY_SQUAD_TOOLTIP),
        )

        resupply_all_squads_button = ttk.Button(
            actions_frame, text=RESUPPLY_ALL_BUTTON, command=self.resupply_all_squads
        )
        resupply_all_squads_button.pack(pady=PADY_SMALL, padx=PADX_SMALL, fill=FILL_X)
        self.create_tooltip(
            resupply_all_squads_button,
            text=(RESUPPLY_ALL_TOOLTIP),
        )

        add_missing_squad_members_button = ttk.Button(
            actions_frame,
            text=ADD_MISSING_MEMBERS_BUTTON,
            command=self.add_missing_squad_members,
        )
        add_missing_squad_members_button.pack(
            pady=PADY_SMALL, padx=PADX_SMALL, fill=FILL_X
        )
        self.create_tooltip(
            add_missing_squad_members_button,
            text=(ADD_MISSING_MEMBERS_TOOLTIP),
        )

    def create_inventory_manager_console_frame_content(
        self, console_frame: ttk.LabelFrame
    ) -> None:
        """Create console output frame content.

        Args:
            console_frame (ttk.LabelFrame): The console frame to contain output
        """
        self.create_generic_console_frame_content(console_frame)

    def prepare_manager(self) -> None:
        """Initialize the InventoryManager with selected file paths."""
        if (
            not self.game_install_dir and not self.data_dir_path
        ) or not self.campaign_file_path:
            self.logger.log(SPECIFY_DIRECTORIES_MSG)
            return

        self.inventory_manager = InventoryManager(
            game_install_dir_path=self.game_install_dir,
            campaign_file_path=self.campaign_file_path,
            data_dir_path=self.data_dir_path,
            logger=self.logger,
        )

        self.inventory_manager.prepare_squads_and_inventories()

        self.logger.log(INVENTORY_MANAGER_INITIALIZED_MSG)

        self.populate_gui_elements_with_data()
        self.update_resources(
            self.inventory_manager.knowledge_base.campaign_status_info.mp,
            self.inventory_manager.knowledge_base.campaign_status_info.ap,
        )

    def populate_gui_elements_with_data(self) -> None:
        """Populate GUI controls with squad and inventory data."""
        squad_names = [
            squad_info.squad_name for squad_info in self.inventory_manager.squads
        ]
        self.squad_combo[COMBOBOX_VALUES_KEY] = squad_names
        if self.squad_combo.current() == -1:
            self.squad_combo.current(0)

        squad_id = self.squad_combo.current()
        squad_members = self.inventory_manager.squads[squad_id].squad_members
        self.squad_member_combo[COMBOBOX_VALUES_KEY] = squad_members
        if self.squad_member_combo.current() == -1:
            self.squad_member_combo.current(0)

        self.show_selected_unit_info(
            self.inventory_manager, squad_id, self.squad_member_combo.get()
        )

    def squad_selected(self, _: tk.Event) -> None:
        """Handle squad selection event.

        Args:
            _ (tk.Event): The event object (not used)
        """
        squad_id = self.squad_combo.current()
        squad_members = self.inventory_manager.squads[squad_id].squad_members
        self.squad_member_combo[COMBOBOX_VALUES_KEY] = squad_members
        self.squad_member_combo.current(0)
        self.show_selected_unit_info(
            self.inventory_manager, squad_id, self.squad_member_combo.get()
        )

    def unit_selected(self, _: tk.Event) -> None:
        """Handle unit selection event.

        Args:
            _ (tk.Event): The event object (not used)
        """
        self.show_selected_unit_info(
            self.inventory_manager,
            self.squad_combo.current(),
            self.squad_member_combo.get(),
        )

    def show_selected_unit_info(
        self, game_manager: GameManager, squad_id: int, squad_member_id: str
    ) -> None:
        """Show selected unit information.

        Args:
            squad_member_id (str): The ID of the squad member to display
        """
        unit_name, unit_type, unit_inventory = self.get_selected_unit_info(
            game_manager, squad_id, squad_member_id
        )

        self.unit_name_label.config(text=unit_name)
        self.unit_type_label.config(text=unit_type)

        unit_inventory.count_items_in_inventory()
        unit_inventory_counts = unit_inventory.item_counts

        lines = []
        for key, value in unit_inventory_counts.items():
            lines.append(f"{key}: {value}")

        unit_inventory_text = "\n".join(lines)
        self.update_unit_details(unit_inventory_text)

    def update_unit_details(self, details_text: str) -> None:
        """Update unit details display.

        Args:
            details_text (str): The text to display in the unit details
        """
        self.unit_inventory_text.config(state=TK_NORMAL)
        self.unit_inventory_text.delete(TEXT_START_INDEX, TK_END)
        self.unit_inventory_text.insert(TK_END, details_text)
        self.unit_inventory_text.config(state=TK_DISABLED)

    def resupply_squad_member(self) -> None:
        """Resupply inventory for the currently selected squad member."""
        squad_id = self.squad_combo.current()
        squad_member_id = self.squad_member_combo.get()
        if not squad_member_id:
            self.logger.log(SELECT_SQUAD_MEMBER_MSG)
            return

        self.inventory_manager.refill_squad_member_inventory(
            squad_id=squad_id, squad_member_id=squad_member_id
        )

        self.show_selected_unit_info(self.inventory_manager, squad_id, squad_member_id)
        self.update_resources(
            self.inventory_manager.knowledge_base.campaign_status_info.mp,
            self.inventory_manager.knowledge_base.campaign_status_info.ap,
        )

    def resupply_squad(self) -> None:
        """Resupply inventories for all members of the currently selected squad."""
        squad_id = self.squad_combo.current()
        if not self.inventory_manager.squads_inventories[squad_id].inventories:
            self.logger.log(NO_SQUAD_MEMBERS_MSG)
            return

        for squad_member_id in self.inventory_manager.squads_inventories[
            squad_id
        ].inventories:
            self.inventory_manager.refill_squad_member_inventory(
                squad_id=squad_id, squad_member_id=squad_member_id
            )

        if self.squad_member_combo.get():
            self.show_selected_unit_info(
                self.inventory_manager, squad_id, self.squad_member_combo.get()
            )
        self.update_resources(
            self.inventory_manager.knowledge_base.campaign_status_info.mp,
            self.inventory_manager.knowledge_base.campaign_status_info.ap,
        )

    def resupply_all_squads(self) -> None:
        """Resupply inventories for all members in all squads."""
        if not self.inventory_manager.squads_inventories:
            self.logger.log(NO_SQUADS_TO_RESUPPLY_MSG)
            return

        for squad_id, squad_inventory in enumerate(
            self.inventory_manager.squads_inventories
        ):
            for squad_member_id in squad_inventory.inventories:
                self.inventory_manager.refill_squad_member_inventory(
                    squad_id=squad_id, squad_member_id=squad_member_id
                )

        if self.squad_member_combo.get():
            self.show_selected_unit_info(
                self.inventory_manager,
                self.squad_combo.current(),
                self.squad_member_combo.get(),
            )

        self.update_resources(
            self.inventory_manager.knowledge_base.campaign_status_info.mp,
            self.inventory_manager.knowledge_base.campaign_status_info.ap,
        )

    def add_missing_squad_members(self) -> None:
        """Add missing squad members to the currently selected squad."""
        squad_id = self.squad_combo.current()
        if not self.inventory_manager.squads_inventories[squad_id].inventories:
            self.logger.log(NO_SQUAD_MEMBERS_TO_ADD_MSG)
            return

        self.inventory_manager.refill_missing_squad_members(squad_id)

        self.populate_gui_elements_with_data()

        self.update_resources(
            self.inventory_manager.knowledge_base.campaign_status_info.mp,
            self.inventory_manager.knowledge_base.campaign_status_info.ap,
        )

    def save_changes(self) -> None:
        """Save inventory modifications to campaign file."""
        if not self.inventory_manager:
            self.logger.log(NO_MANAGER_INITIALIZED_MSG)
            return

        confirm = self.show_confirmation_dialog(
            title=SAVE_CHANGES_TITLE,
            message=SAVE_CHANGES_CONFIRMATION_MSG,
        )

        if not confirm:
            self.logger.log(SAVE_CANCELLED_MSG)
            return

        try:
            self.inventory_manager.save_changes()
            self.logger.log(CHANGES_SAVED_MSG)

            self.inventory_manager.prepare_squads_and_inventories()
            self.populate_gui_elements_with_data()
            self.update_resources(
                self.inventory_manager.knowledge_base.campaign_status_info.mp,
                self.inventory_manager.knowledge_base.campaign_status_info.ap,
            )
        except KeyError as e:
            self.logger.log(f"{ERROR_SAVING_CHANGES_MSG} {str(e)}")

    def update_resources(self, mp: float, ap: float) -> None:
        """Update the resource displays.

        Args:
            mp (float): Manpower value
            ap (float): Action Points value
        """
        self.mp_resource.set(round(mp, RESOURCE_DECIMAL_PRECISION))
        self.ap_resource.set(round(ap, RESOURCE_DECIMAL_PRECISION))

        # Optional: Add color indicator if resources are low
        mp_color = MP_COLOR_LOW if mp < MP_LOW_THRESHOLD else MP_COLOR_HIGH
        ap_color = AP_COLOR_LOW if ap < AP_LOW_THRESHOLD else AP_COLOR_HIGH

        # Apply color (this requires configuring styles)
        style = ttk.Style()
        style.configure(MP_LABEL_STYLE, foreground=mp_color, font=RESOURCE_FONT)
        style.configure(AP_LABEL_STYLE, foreground=ap_color, font=RESOURCE_FONT)
