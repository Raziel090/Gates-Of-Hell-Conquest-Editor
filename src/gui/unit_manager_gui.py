"""Unit Manager GUI module for managing and moving units between squads."""

from tkinter import ttk
import tkinter as tk
from src.gui.manager_gui import ManagerGUI
from src.managers.unit_manager import UnitManager


# UI Text Constants
MANAGER_NAME = "Unit Manager"
TAB_TITLE = "Unit Manager"

# Frame Labels
CONTROLS_FRAME_LABEL = "Controls"
SELECTION_FRAME_LABEL = "Selection"
CONSOLE_OUTPUT_FRAME_LABEL = "Console Output"
ACTIONS_FRAME_LABEL = "Actions"

# UI Labels
SELECT_BASE_SQUAD_LABEL = "Select Base Squad:"
SELECT_BASE_SQUAD_MEMBER_LABEL = "Select Base Squad Member:"
SELECT_TARGET_SQUAD_LABEL = "Select Target Squad:"
SELECT_TARGET_SQUAD_MEMBER_LABEL = "Select Target Squad Member:"
UNIT_TYPE_LABEL = "Unit Type:"
UNIT_NAME_LABEL = "Unit Name:"
UNKNOWN_VALUE = "Unknown"

# Button Labels
MOVE_UNIT_TO_SQUAD_BUTTON = "Move Unit To Squad"
EXCHANGE_UNITS_BUTTON = "Exchange Units"

# Tooltip Messages
MOVE_UNIT_TOOLTIP = "Move currently selected unit (squad member) to the target squad.\n"
EXCHANGE_UNITS_TOOLTIP = "Exchange currently selected unit (squad member) with the target unit (squad member).\n"

# Log Messages
UNIT_MANAGER_STARTED_MSG = "Unit Manager started!"
UNIT_MANAGER_INITIALIZED_MSG = "Unit Manager initialized successfully."
NO_UNIT_SELECTED_MSG = "No unit selected to move."
UNITS_REQUIRED_FOR_EXCHANGE_MSG = "Both units must be selected to perform an exchange."
CANNOT_EXCHANGE_WITH_SELF_MSG = "Cannot exchange a unit with itself."
NO_MANAGER_INITIALIZED_MSG = "No unit manager initialized. Cannot save changes."
SAVE_CANCELLED_MSG = "Save operation cancelled."
CHANGES_SAVED_MSG = "Changes saved successfully."

# Dialog Messages
SAVE_CHANGES_TITLE = "Save Changes"
SAVE_CHANGES_MESSAGE = "Are you sure you want to save these changes to the campaign file?\n\nThis will overwrite the existing file."

# Cache Keys
GAME_INSTALL_DIR_KEY = "game_install_dir"
CAMPAIGN_FILE_PATH_KEY = "campaign_file_path"
DATA_DIR_PATH_KEY = "data_dir_path"

# Error Messages
SPECIFY_DIRECTORIES_MSG = (
    "Please specify Game Installation Directory or Data Directory and Campaign File."
)
ERROR_SAVING_CHANGES_MSG = "Error saving changes: {}"

# Widget positioning constants
SIDE_LEFT = "left"
FILL_BOTH = "both"
FILL_X = "x"
ANCHOR_WEST = "w"

# Event constants
COMBOBOX_SELECTED_EVENT = "<<ComboboxSelected>>"

# UI Configuration
READONLY_STATE = "readonly"
COMBOBOX_WIDTH = 30
HORIZONTAL_ORIENTATION = "horizontal"
COMBOBOX_VALUES_KEY = "value"


class UnitManagerGUI(ManagerGUI):
    """Unit Manager GUI class for handling unit operations and squad management.

    Provides interface for moving and exchanging units between squads.
    """

    def __init__(self, parent_notebook: ttk.Notebook) -> None:
        """Initialize the Unit Manager GUI.

        Args:
            parent_notebook (ttk.Notebook): The parent notebook widget
        """
        super().__init__(parent_notebook=parent_notebook)

        self.manager_name = MANAGER_NAME

    def create_gui(self) -> None:
        """Create the Unit Manager GUI interface."""
        # Create unit manager tab
        unit_manager_tab = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(unit_manager_tab, text=TAB_TITLE)

        self.create_unit_manager_tab_content(unit_manager_tab)

    def create_unit_manager_tab_content(self, tab_frame: ttk.Frame) -> None:
        """Create content for the unit manager tab.

        Args:
            tab_frame (ttk.Frame): The tab frame to contain the content
        """
        # Create parent frame to hold different elements of unit manager
        parent_frame = ttk.Frame(tab_frame)
        parent_frame.pack(fill=FILL_BOTH, expand=True)

        # Create left frame for buttons and labels
        left_frame = ttk.LabelFrame(parent_frame, text=CONTROLS_FRAME_LABEL)
        left_frame.pack(side=SIDE_LEFT, fill=FILL_BOTH, expand=True, padx=5, pady=10)

        # Create middle frame for comboboxes and interactive elements
        middle_frame = ttk.LabelFrame(parent_frame, text=SELECTION_FRAME_LABEL)
        middle_frame.pack(side=SIDE_LEFT, fill=FILL_BOTH, expand=True, padx=5, pady=10)

        # Create console frame (right side)
        console_frame = ttk.LabelFrame(parent_frame, text=CONSOLE_OUTPUT_FRAME_LABEL)
        console_frame.pack(side=SIDE_LEFT, fill=FILL_BOTH, expand=True, padx=5, pady=10)

        self.create_unit_manager_left_frame_content(left_frame)
        self.create_unit_manager_middle_frame_content(middle_frame)
        self.create_unit_manager_console_frame_content(console_frame)

        # Write initial message to console
        self.logger.log(UNIT_MANAGER_STARTED_MSG)

        # Load cache after logger is initialized
        cached_settings = self.load_cache()
        self.game_install_dir = cached_settings.get(GAME_INSTALL_DIR_KEY, "")
        self.campaign_file_path = cached_settings.get(CAMPAIGN_FILE_PATH_KEY, "")
        self.data_dir_path = cached_settings.get(DATA_DIR_PATH_KEY, self.data_dir_path)

        # Update UI with cached values
        self.update_ui_from_cache()

        # Prepare the manager with cached values if possible
        self.prepare_manager_from_cache()

    def create_unit_manager_left_frame_content(
        self, left_frame: ttk.LabelFrame
    ) -> None:
        """Create content for the left control frame.

        Args:
            left_frame (ttk.LabelFrame): The left frame container
        """
        self.create_generic_data_management_content(left_frame)

    def create_unit_manager_middle_frame_content(
        self, middle_frame: ttk.LabelFrame
    ) -> None:
        """Create content for the middle selection frame.

        Args:
            middle_frame (ttk.LabelFrame): The middle frame container
        """
        # === BASE SQUAD RELATED ELEMENTS ===
        # Base squad selection
        ttk.Label(middle_frame, text=SELECT_BASE_SQUAD_LABEL).pack(
            pady=5, padx=10, anchor=ANCHOR_WEST
        )
        self.base_squad_combo = ttk.Combobox(
            middle_frame, state=READONLY_STATE, width=COMBOBOX_WIDTH
        )
        self.base_squad_combo.pack(pady=5, padx=10, fill=FILL_X)
        self.base_squad_combo.bind(COMBOBOX_SELECTED_EVENT, self.base_squad_selected)

        # Base squad member selection
        ttk.Label(middle_frame, text=SELECT_BASE_SQUAD_MEMBER_LABEL).pack(
            pady=5, padx=10, anchor=ANCHOR_WEST
        )
        self.base_squad_member_combo = ttk.Combobox(
            middle_frame, state=READONLY_STATE, width=COMBOBOX_WIDTH
        )
        self.base_squad_member_combo.pack(pady=5, padx=10, fill=FILL_X)
        self.base_squad_member_combo.bind(
            COMBOBOX_SELECTED_EVENT, self.base_unit_selected
        )

        # Create a unit info container frame
        unit_info_frame = ttk.Frame(middle_frame)
        unit_info_frame.pack(fill=FILL_X, padx=10, pady=5)

        # Unit type row
        unit_type_frame = ttk.Frame(unit_info_frame)
        unit_type_frame.pack(fill=FILL_X, pady=2)
        ttk.Label(unit_type_frame, text=UNIT_TYPE_LABEL).pack(side=SIDE_LEFT)
        self.base_unit_type_label = ttk.Label(unit_type_frame, text=UNKNOWN_VALUE)
        self.base_unit_type_label.pack(side=SIDE_LEFT, padx=(26, 0))

        # Unit name row
        unit_name_frame = ttk.Frame(unit_info_frame)
        unit_name_frame.pack(fill=FILL_X, pady=2)
        ttk.Label(unit_name_frame, text=UNIT_NAME_LABEL).pack(side=SIDE_LEFT)
        self.base_unit_name_label = ttk.Label(unit_name_frame, text=UNKNOWN_VALUE)
        self.base_unit_name_label.pack(side=SIDE_LEFT, padx=(20, 0))

        # Add a separator
        ttk.Separator(middle_frame, orient=HORIZONTAL_ORIENTATION).pack(
            fill=FILL_X, pady=15, padx=10
        )

        # === TARGET SQUAD RELATED ELEMENTS ===
        # Target squad selection
        ttk.Label(middle_frame, text=SELECT_TARGET_SQUAD_LABEL).pack(
            pady=5, padx=10, anchor=ANCHOR_WEST
        )
        self.target_squad_combo = ttk.Combobox(
            middle_frame, state=READONLY_STATE, width=COMBOBOX_WIDTH
        )
        self.target_squad_combo.pack(pady=5, padx=10, fill=FILL_X)
        self.target_squad_combo.bind(
            COMBOBOX_SELECTED_EVENT, self.target_squad_selected
        )

        # Target squad member selection
        ttk.Label(middle_frame, text=SELECT_TARGET_SQUAD_MEMBER_LABEL).pack(
            pady=5, padx=10, anchor=ANCHOR_WEST
        )
        self.target_squad_member_combo = ttk.Combobox(
            middle_frame, state=READONLY_STATE, width=COMBOBOX_WIDTH
        )
        self.target_squad_member_combo.pack(pady=5, padx=10, fill=FILL_X)
        self.target_squad_member_combo.bind(
            COMBOBOX_SELECTED_EVENT, self.target_unit_selected
        )

        # Create a unit info container frame
        unit_info_frame = ttk.Frame(middle_frame)
        unit_info_frame.pack(fill=FILL_X, padx=10, pady=5)

        # Unit type row
        unit_type_frame = ttk.Frame(unit_info_frame)
        unit_type_frame.pack(fill=FILL_X, pady=2)
        ttk.Label(unit_type_frame, text=UNIT_TYPE_LABEL).pack(side=SIDE_LEFT)
        self.target_unit_type_label = ttk.Label(unit_type_frame, text=UNKNOWN_VALUE)
        self.target_unit_type_label.pack(side=SIDE_LEFT, padx=(26, 0))

        # Unit name row
        unit_name_frame = ttk.Frame(unit_info_frame)
        unit_name_frame.pack(fill=FILL_X, pady=2)
        ttk.Label(unit_name_frame, text=UNIT_NAME_LABEL).pack(side=SIDE_LEFT)
        self.target_unit_name_label = ttk.Label(unit_name_frame, text=UNKNOWN_VALUE)
        self.target_unit_name_label.pack(side=SIDE_LEFT, padx=(20, 0))

        # Add a separator
        ttk.Separator(middle_frame, orient=HORIZONTAL_ORIENTATION).pack(
            fill=FILL_X, pady=15, padx=10
        )
        # Inventory actions frame
        actions_frame = ttk.LabelFrame(middle_frame, text=ACTIONS_FRAME_LABEL)
        actions_frame.pack(pady=10, padx=10, fill=FILL_X)

        # Action buttons
        move_unit_to_squad_button = ttk.Button(
            actions_frame,
            text=MOVE_UNIT_TO_SQUAD_BUTTON,
            command=self.move_unit_to_squad,
        )
        move_unit_to_squad_button.pack(pady=5, padx=5, fill=FILL_X)
        self.create_tooltip(
            move_unit_to_squad_button,
            text=MOVE_UNIT_TOOLTIP,
        )

        exchange_units_button = ttk.Button(
            actions_frame,
            text=EXCHANGE_UNITS_BUTTON,
            command=self.exchange_units,
        )
        exchange_units_button.pack(pady=5, padx=5, fill=FILL_X)
        self.create_tooltip(
            exchange_units_button,
            text=EXCHANGE_UNITS_TOOLTIP,
        )

    def create_unit_manager_console_frame_content(
        self, console_frame: ttk.LabelFrame
    ) -> None:
        """Create console output frame content.

        Args:
            console_frame (ttk.LabelFrame): The console frame container
        """
        self.create_generic_console_frame_content(console_frame)

    def prepare_manager(self) -> None:
        """Initialize the UnitManager with selected file paths."""
        if (
            not self.game_install_dir and not self.data_dir_path
        ) or not self.campaign_file_path:
            self.logger.log(SPECIFY_DIRECTORIES_MSG)
            return

        self.unit_manager = UnitManager(
            game_install_dir_path=self.game_install_dir,
            campaign_file_path=self.campaign_file_path,
            data_dir_path=self.data_dir_path,
            logger=self.logger,
        )

        self.unit_manager.prepare_squads_and_inventories(keep_deceased_members=True)

        self.logger.log(UNIT_MANAGER_INITIALIZED_MSG)

        self.populate_gui_elements_with_data()

    def populate_gui_elements_with_data(self) -> None:
        """Populate GUI controls with squad and unit data."""
        squad_names = [squad_info.squad_name for squad_info in self.unit_manager.squads]
        self.base_squad_combo[COMBOBOX_VALUES_KEY] = squad_names
        self.base_squad_combo.current(0)
        self.base_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            0
        ].squad_members
        self.base_squad_member_combo.current(0)
        self.target_squad_combo[COMBOBOX_VALUES_KEY] = squad_names
        self.target_squad_combo.current(1)
        self.target_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            1
        ].squad_members
        self.target_squad_member_combo.current(0)

    def base_squad_selected(self, click_event: tk.Event) -> None:
        """Handle squad selection.

        Args:
            click_event (tk.Event): The event object (not used)
        """
        squad_id: int = click_event.widget.current()
        self.base_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            squad_id
        ].squad_members
        self.base_squad_member_combo.current(0)
        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager, squad_id, self.base_squad_member_combo.get()
        )
        self.base_unit_name_label.config(text=unit_name)
        self.base_unit_type_label.config(text=unit_type)

        squad_names = [squad_info.squad_name for squad_info in self.unit_manager.squads]
        squad_names.pop(squad_id)
        self.target_squad_combo[COMBOBOX_VALUES_KEY] = squad_names

        target_squad_id = self.target_squad_combo.current()

        if self.target_squad_combo.current() == -1:
            self.target_squad_combo.current(0)
        if target_squad_id >= squad_id:
            target_squad_id += 1
        if target_squad_id == squad_id:
            self.target_squad_combo.current(0)

        target_squad_id = self.target_squad_combo.current()
        if target_squad_id >= squad_id:
            target_squad_id += 1

        self.target_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            target_squad_id
        ].squad_members

        target_squad_member_id = self.target_squad_member_combo.current()
        if target_squad_member_id == -1:
            self.target_squad_member_combo.current(0)

        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager, target_squad_id, self.target_squad_member_combo.get()
        )
        self.target_unit_name_label.config(text=unit_name)
        self.target_unit_type_label.config(text=unit_type)

    def base_unit_selected(self, _: tk.Event) -> None:
        """Handle base unit selection event.

        Args:
            _ (tk.Event): The event object (not used)
        """
        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager,
            self.base_squad_combo.current(),
            self.base_squad_member_combo.get(),
        )
        self.base_unit_name_label.config(text=unit_name)
        self.base_unit_type_label.config(text=unit_type)

    def target_squad_selected(self, click_event: tk.Event) -> None:
        """Handle target squad selection event.

        Args:
            click_event (tk.Event): The event object containing selection data
        """
        squad_id: int = click_event.widget.current()

        if squad_id >= self.base_squad_combo.current():
            squad_id += 1

        self.target_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            squad_id
        ].squad_members
        self.target_squad_member_combo.current(0)
        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager, squad_id, self.target_squad_member_combo.get()
        )
        self.target_unit_name_label.config(text=unit_name)
        self.target_unit_type_label.config(text=unit_type)

    def target_unit_selected(self, _: tk.Event) -> None:
        """Handle target unit selection event.

        Args:
            _ (tk.Event): The event object (not used)
        """
        target_squad_id = self.target_squad_combo.current()
        if target_squad_id >= self.base_squad_combo.current():
            target_squad_id += 1

        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager,
            target_squad_id,
            self.target_squad_member_combo.get(),
        )
        self.target_unit_name_label.config(text=unit_name)
        self.target_unit_type_label.config(text=unit_type)

    def move_unit_to_squad(self) -> None:
        """Move selected unit from base squad to target squad."""
        base_squad_id = self.base_squad_combo.current()
        target_squad_id = self.target_squad_combo.current()
        if target_squad_id >= base_squad_id:
            target_squad_id += 1
        base_unit_id = self.base_squad_member_combo.get()

        if not base_unit_id:
            self.logger.log(NO_UNIT_SELECTED_MSG)
            return

        base_squad_name = self.unit_manager.squads[base_squad_id].squad_name
        target_squad_name = self.unit_manager.squads[target_squad_id].squad_name
        base_unit_name, _, _ = self.get_selected_unit_info(
            self.unit_manager,
            base_squad_id,
            base_unit_id,
        )

        self.unit_manager.move_unit(
            base_squad_id, base_unit_id, target_squad_id, None, None
        )
        self.logger.log(
            f"Moved unit '{base_unit_id}' ({base_unit_name}) from squad {base_squad_name} to {target_squad_name}."
        )

        self.unit_manager.prepare_squads_and_inventories(keep_deceased_members=True)
        self.update_ui_after_action()

    def exchange_units(self) -> None:
        """Exchange positions of base unit and target unit."""
        base_squad_id = self.base_squad_combo.current()
        target_squad_id = self.target_squad_combo.current()
        if target_squad_id >= base_squad_id:
            target_squad_id += 1
        base_unit_id = self.base_squad_member_combo.get()
        target_unit_id = self.target_squad_member_combo.get()

        if not base_unit_id or not target_unit_id:
            self.logger.log(UNITS_REQUIRED_FOR_EXCHANGE_MSG)
            return

        base_squad_name = self.unit_manager.squads[base_squad_id].squad_name
        target_squad_name = self.unit_manager.squads[target_squad_id].squad_name
        base_unit_name, _, _ = self.get_selected_unit_info(
            self.unit_manager,
            base_squad_id,
            base_unit_id,
        )
        target_unit_name, _, _ = self.get_selected_unit_info(
            self.unit_manager,
            target_squad_id,
            target_unit_id,
        )

        if base_unit_id == target_unit_id and base_squad_id == target_squad_id:
            self.logger.log(CANNOT_EXCHANGE_WITH_SELF_MSG)
            return

        self.unit_manager.move_unit(
            base_squad_id,
            base_unit_id,
            target_squad_id,
            target_unit_id,
            self.target_squad_member_combo.current(),
        )
        self.logger.log(
            f"Exchanged unit '{base_unit_id}' ({base_unit_name}) from squad {base_squad_name} with unit '{target_unit_id}' ({target_unit_name}) from squad {target_squad_name}."
        )

        self.unit_manager.prepare_squads_and_inventories(keep_deceased_members=True)
        self.update_ui_after_action()

    def update_ui_after_action(self) -> None:
        """Refresh UI elements after unit operations."""
        base_squad_id = self.base_squad_combo.current()
        target_squad_id = self.target_squad_combo.current()

        if target_squad_id >= base_squad_id:
            target_squad_id += 1

        self.base_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            base_squad_id
        ].squad_members
        self.base_squad_member_combo.current(0)
        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager, base_squad_id, self.base_squad_member_combo.get()
        )
        self.base_unit_name_label.config(text=unit_name)
        self.base_unit_type_label.config(text=unit_type)

        self.target_squad_member_combo[COMBOBOX_VALUES_KEY] = self.unit_manager.squads[
            target_squad_id
        ].squad_members
        self.target_squad_member_combo.current(0)
        unit_name, unit_type, _ = self.get_selected_unit_info(
            self.unit_manager, target_squad_id, self.target_squad_member_combo.get()
        )
        self.target_unit_name_label.config(text=unit_name)
        self.target_unit_type_label.config(text=unit_type)

    def save_changes(self) -> None:
        """Save unit modifications to campaign file."""
        if not self.unit_manager:
            self.logger.log(NO_MANAGER_INITIALIZED_MSG)
            return

        confirm = self.show_confirmation_dialog(
            title=SAVE_CHANGES_TITLE,
            message=SAVE_CHANGES_MESSAGE,
        )

        if not confirm:
            self.logger.log(SAVE_CANCELLED_MSG)
            return

        try:
            self.unit_manager.save_changes()
            self.logger.log(CHANGES_SAVED_MSG)
            self.prepare_manager()
        except Exception as e:
            self.logger.log(ERROR_SAVING_CHANGES_MSG.format(str(e)))
