"""Vehicle appearance manager GUI for Entity visual customization."""

from tkinter import ttk
import tkinter as tk

from src.constants import (
    CAMPAIGN_FILE_PATH_KEY,
    DATA_DIR_PATH_KEY,
    GAME_INSTALL_DIR_KEY,
    VEHICLE_ENUMERATOR_DIGIT_FOLDERS,
)
from src.gui.manager_gui import ManagerGUI
from src.managers.vehicle_appearance_manager import (
    VehicleAppearanceEntity,
    VehicleAppearanceManager,
)


MANAGER_NAME = "Vehicle Appearance Manager"
TAB_TITLE = "Vehicle Appearance"

CONTROLS_FRAME_LABEL = "Controls"
SELECTION_FRAME_LABEL = "Vehicle Appearance"
CONSOLE_OUTPUT_FRAME_LABEL = "Console Output"
APPEARANCE_ACTIONS_FRAME_LABEL = "Appearance Actions"

SELECT_VEHICLE_LABEL = "Select Vehicle Entity:"
ARMOR_STATUS_LABEL = "Armor Damage:"
ENUMERATOR_STATUS_LABEL = "Enumerator:"
NUMBER_LABEL = "Number (0-999):"
DIGIT_FOLDER_LABEL = "Digit Folder:"

ARMOR_PRESENT_TEXT = "Present"
ARMOR_ABSENT_TEXT = "None"
ENUMERATOR_PRESENT_TEXT = "Present"
ENUMERATOR_ABSENT_TEXT = "Not present"
UNKNOWN_VALUE = "Unknown"

REMOVE_ARMOR_DAMAGE_BUTTON = "Make Vehicle Look Undamaged"
APPLY_ENUMERATOR_BUTTON = "Update Vehicle Markings"

REMOVE_ARMOR_TOOLTIP = "Clear visible armor damage for the selected vehicle.\n"
APPLY_ENUMERATOR_TOOLTIP = (
    "Set the number and marking style shown on the selected vehicle.\n"
)

VEHICLE_MANAGER_STARTED_MSG = "Vehicle Appearance Manager started!"
VEHICLE_MANAGER_INITIALIZED_MSG = "Vehicle Appearance Manager initialized successfully."
NO_MANAGER_INITIALIZED_MSG = "No vehicle appearance manager initialized."
NO_ENTITY_SELECTED_MSG = "No vehicle entity selected."
NO_ENUMERATOR_MSG = "Selected vehicle has no enumerator section."
ARMOR_REMOVED_MSG = "Armor section removed successfully."
ARMOR_NOT_FOUND_MSG = "No Armor section found for selected vehicle."
ENUMERATOR_UPDATED_MSG = "Enumerator updated successfully."
SAVE_CANCELLED_MSG = "Save operation cancelled."
CHANGES_SAVED_MSG = "Changes saved successfully."
ERROR_SAVING_CHANGES_MSG = "Error saving changes: {}"
SPECIFY_DIRECTORIES_MSG = (
    "Please specify Game Installation Directory or Data Directory and Campaign File."
)

SAVE_CHANGES_TITLE = "Save Changes"
SAVE_CHANGES_MESSAGE = "Are you sure you want to save these changes to the campaign file?\n\nThis will overwrite the existing file."

SIDE_LEFT = "left"
FILL_BOTH = "both"
FILL_X = "x"
ANCHOR_WEST = "w"
READONLY_STATE = "readonly"
COMBOBOX_VALUES_KEY = "value"
TK_DISABLED = "disabled"
TK_NORMAL = "normal"


class VehicleAppearanceManagerGUI(ManagerGUI):
    """GUI tab for editing Entity vehicle appearance settings."""

    def __init__(self, parent_notebook: ttk.Notebook) -> None:
        super().__init__(parent_notebook=parent_notebook)
        self.manager_name = MANAGER_NAME
        self.entities_by_display_name: dict[str, VehicleAppearanceEntity] = {}

    def create_gui(self) -> None:
        vehicle_tab = ttk.Frame(self.parent_notebook)
        self.parent_notebook.add(vehicle_tab, text=TAB_TITLE)
        self.create_vehicle_tab_content(vehicle_tab)

    def create_vehicle_tab_content(self, tab_frame: ttk.Frame) -> None:
        parent_frame = ttk.Frame(tab_frame)
        parent_frame.pack(fill=FILL_BOTH, expand=True)

        left_frame, middle_frame, console_frame = self.create_standard_tab_layout(
            parent_frame,
            left_title=CONTROLS_FRAME_LABEL,
            middle_title=SELECTION_FRAME_LABEL,
            console_title=CONSOLE_OUTPUT_FRAME_LABEL,
            middle_width=320,
            middle_height=400,
        )

        self.create_vehicle_left_frame_content(left_frame)
        self.create_vehicle_middle_frame_content(middle_frame)
        self.create_vehicle_console_frame_content(console_frame)

        self._log(VEHICLE_MANAGER_STARTED_MSG)

        cached_settings = self.load_cache()
        self.game_install_dir = cached_settings.get(GAME_INSTALL_DIR_KEY, "")
        self.campaign_file_path = cached_settings.get(CAMPAIGN_FILE_PATH_KEY, "")
        self.data_dir_path = cached_settings.get(DATA_DIR_PATH_KEY, self.data_dir_path)

        self.update_ui_from_cache()
        self.prepare_manager_from_cache()

    def create_vehicle_left_frame_content(self, left_frame: ttk.LabelFrame) -> None:
        self.create_generic_data_management_content(left_frame)

    def create_vehicle_middle_frame_content(self, middle_frame: ttk.LabelFrame) -> None:
        ttk.Label(middle_frame, text=SELECT_VEHICLE_LABEL).pack(
            pady=5, padx=10, anchor=ANCHOR_WEST
        )
        self.entity_combo = ttk.Combobox(middle_frame, state=READONLY_STATE, width=40)
        self.entity_combo.pack(pady=5, padx=10, fill=FILL_X)
        self.entity_combo.bind("<<ComboboxSelected>>", self.entity_selected)

        status_frame = ttk.Frame(middle_frame)
        status_frame.pack(fill=FILL_X, padx=10, pady=6)

        ttk.Label(status_frame, text=ARMOR_STATUS_LABEL).grid(row=0, column=0, sticky=ANCHOR_WEST)
        self.armor_status_value_label = ttk.Label(status_frame, text=UNKNOWN_VALUE)
        self.armor_status_value_label.grid(row=0, column=1, sticky=ANCHOR_WEST, padx=(12, 0))

        ttk.Label(status_frame, text=ENUMERATOR_STATUS_LABEL).grid(row=1, column=0, sticky=ANCHOR_WEST)
        self.enumerator_status_value_label = ttk.Label(status_frame, text=UNKNOWN_VALUE)
        self.enumerator_status_value_label.grid(row=1, column=1, sticky=ANCHOR_WEST, padx=(12, 0))

        ttk.Separator(middle_frame, orient="horizontal").pack(fill=FILL_X, padx=10, pady=10)

        ttk.Label(middle_frame, text=NUMBER_LABEL).pack(pady=5, padx=10, anchor=ANCHOR_WEST)
        number_validator = (middle_frame.register(self._validate_number_input), "%P")
        self.number_entry = ttk.Entry(
            middle_frame,
            validate="key",
            validatecommand=number_validator,
        )
        self.number_entry.pack(pady=5, padx=10, fill=FILL_X)

        ttk.Label(middle_frame, text=DIGIT_FOLDER_LABEL).pack(pady=5, padx=10, anchor=ANCHOR_WEST)
        self.digit_folder_combo = ttk.Combobox(middle_frame, state=READONLY_STATE)
        self.digit_folder_combo[COMBOBOX_VALUES_KEY] = VEHICLE_ENUMERATOR_DIGIT_FOLDERS
        self.digit_folder_combo.pack(pady=5, padx=10, fill=FILL_X)
        if VEHICLE_ENUMERATOR_DIGIT_FOLDERS:
            self.digit_folder_combo.current(0)

        actions_frame = ttk.LabelFrame(middle_frame, text=APPEARANCE_ACTIONS_FRAME_LABEL)
        actions_frame.pack(pady=10, padx=10, fill=FILL_X)

        remove_armor_button = ttk.Button(
            actions_frame,
            text=REMOVE_ARMOR_DAMAGE_BUTTON,
            command=self.remove_armor_damage,
        )
        remove_armor_button.pack(pady=5, padx=5, fill=FILL_X)
        self.create_tooltip(remove_armor_button, REMOVE_ARMOR_TOOLTIP)

        self.apply_enumerator_button = ttk.Button(
            actions_frame,
            text=APPLY_ENUMERATOR_BUTTON,
            command=self.apply_enumerator,
        )
        self.apply_enumerator_button.pack(pady=5, padx=5, fill=FILL_X)
        self.create_tooltip(self.apply_enumerator_button, APPLY_ENUMERATOR_TOOLTIP)

        self._set_enumerator_controls_enabled(False)

    def create_vehicle_console_frame_content(self, console_frame: ttk.LabelFrame) -> None:
        self.create_generic_console_frame_content(console_frame)

    def prepare_manager(self) -> None:
        if (
            not self.game_install_dir and not self.data_dir_path
        ) or not self.campaign_file_path:
            self._log(SPECIFY_DIRECTORIES_MSG)
            return

        if self.logger is None:
            raise RuntimeError("Console logger is not initialized.")

        self.vehicle_manager = VehicleAppearanceManager(
            game_install_dir_path=self.game_install_dir,
            campaign_file_path=self.campaign_file_path,
            data_dir_path=self.data_dir_path,
            logger=self.logger,
        )

        self.vehicle_manager.prepare_vehicle_entities()
        self._log(VEHICLE_MANAGER_INITIALIZED_MSG)
        self.populate_gui_elements_with_data()

    def populate_gui_elements_with_data(self) -> None:
        self.populate_gui_elements_with_data_preserving_selection()

    def populate_gui_elements_with_data_preserving_selection(
        self, selected_entity_id: str | None = None
    ) -> None:
        entities = self.vehicle_manager.vehicle_entities
        display_names = [entity.display_name for entity in entities]
        self.entities_by_display_name = {
            entity.display_name: entity for entity in entities
        }

        self.entity_combo[COMBOBOX_VALUES_KEY] = display_names
        if display_names:
            selected_index = 0
            if selected_entity_id is not None:
                for idx, entity in enumerate(entities):
                    if entity.entity_id == selected_entity_id:
                        selected_index = idx
                        break

            self.entity_combo.current(selected_index)
            self._update_entity_details(entities[selected_index])
        else:
            self.number_entry.configure(state=TK_NORMAL)
            self.number_entry.delete(0, tk.END)
            self.enumerator_status_value_label.config(text=ENUMERATOR_ABSENT_TEXT)
            self.armor_status_value_label.config(text=UNKNOWN_VALUE)
            if VEHICLE_ENUMERATOR_DIGIT_FOLDERS:
                self.digit_folder_combo.set(VEHICLE_ENUMERATOR_DIGIT_FOLDERS[0])
            self._set_enumerator_controls_enabled(False)

    def entity_selected(self, _: tk.Event) -> None:
        selected_entity = self._get_selected_entity()
        if selected_entity is None:
            return
        self._update_entity_details(selected_entity)

    def _get_selected_entity(self) -> VehicleAppearanceEntity | None:
        display_name = self.entity_combo.get()
        if not display_name:
            return None
        return self.entities_by_display_name.get(display_name)

    def _update_entity_details(self, entity: VehicleAppearanceEntity) -> None:
        armor_status = ARMOR_PRESENT_TEXT if entity.has_armor_section else ARMOR_ABSENT_TEXT
        enumerator_status = (
            ENUMERATOR_PRESENT_TEXT if entity.has_enumerator else ENUMERATOR_ABSENT_TEXT
        )
        self.armor_status_value_label.config(text=armor_status)
        self.enumerator_status_value_label.config(text=enumerator_status)

        # Allow reliable text updates regardless of previous disabled state.
        self.number_entry.configure(state=TK_NORMAL)
        self.number_entry.delete(0, tk.END)
        if entity.number_value is not None:
            self.number_entry.insert(0, entity.number_value)

        if entity.digit_folder_value is not None:
            folder_values = list(self.digit_folder_combo[COMBOBOX_VALUES_KEY])
            if entity.digit_folder_value in folder_values:
                self.digit_folder_combo.set(entity.digit_folder_value)

        self._set_enumerator_controls_enabled(entity.has_enumerator)

    def _set_enumerator_controls_enabled(self, enabled: bool) -> None:
        if enabled:
            self.number_entry.configure(state=TK_NORMAL)
            self.digit_folder_combo.configure(state=READONLY_STATE)
            self.apply_enumerator_button.configure(state=TK_NORMAL)
            return

        self.number_entry.configure(state=TK_DISABLED)
        self.digit_folder_combo.configure(state=TK_DISABLED)
        self.apply_enumerator_button.configure(state=TK_DISABLED)

    def _validate_number_input(self, proposed_value: str) -> bool:
        """Allow only up to three digits for enumerator number entry."""
        if proposed_value == "":
            return True
        if len(proposed_value) > 3:
            return False
        return proposed_value.isdigit()

    def remove_armor_damage(self) -> None:
        if not hasattr(self, "vehicle_manager"):
            self._log(NO_MANAGER_INITIALIZED_MSG)
            return

        selected_entity = self._get_selected_entity()
        if selected_entity is None:
            self._log(NO_ENTITY_SELECTED_MSG)
            return

        removed = self.vehicle_manager.remove_vehicle_armor_damage(
            selected_entity.entity_id
        )
        self.populate_gui_elements_with_data_preserving_selection(
            selected_entity.entity_id
        )
        self._log(ARMOR_REMOVED_MSG if removed else ARMOR_NOT_FOUND_MSG)

    def apply_enumerator(self) -> None:
        if not hasattr(self, "vehicle_manager"):
            self._log(NO_MANAGER_INITIALIZED_MSG)
            return

        selected_entity = self._get_selected_entity()
        if selected_entity is None:
            self._log(NO_ENTITY_SELECTED_MSG)
            return
        if not selected_entity.has_enumerator:
            self._log(NO_ENUMERATOR_MSG)
            return

        try:
            updated = self.vehicle_manager.update_vehicle_enumerator(
                selected_entity.entity_id,
                self.number_entry.get(),
                self.digit_folder_combo.get(),
            )
        except ValueError as error:
            self._log(str(error))
            return

        self.populate_gui_elements_with_data_preserving_selection(
            selected_entity.entity_id
        )
        if updated:
            self._log(ENUMERATOR_UPDATED_MSG)

    def save_changes(self) -> None:
        if not hasattr(self, "vehicle_manager"):
            self._log(NO_MANAGER_INITIALIZED_MSG)
            return

        confirm = self.show_confirmation_dialog(
            title=SAVE_CHANGES_TITLE,
            message=SAVE_CHANGES_MESSAGE,
        )
        if not confirm:
            self._log(SAVE_CANCELLED_MSG)
            return

        try:
            self.vehicle_manager.save_changes()
            self._log(CHANGES_SAVED_MSG)
            self.vehicle_manager.prepare_vehicle_entities()
            selected_entity = self._get_selected_entity()
            selected_entity_id = (
                selected_entity.entity_id if selected_entity is not None else None
            )
            self.populate_gui_elements_with_data_preserving_selection(selected_entity_id)
        except Exception as error:
            self._log(ERROR_SAVING_CHANGES_MSG.format(str(error)))