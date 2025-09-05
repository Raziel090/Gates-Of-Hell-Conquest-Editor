"""Data management for campaign files and game assets extraction."""

import os
from pathlib import Path
import re
import zipfile

from src.console_logger import ConsoleLogger
from src.data_classes import SquadInfo
from src.entity_inventory import EntityInventory
from src.knowledge_base import KnowledgeBase
from src.constants import (
    # File and directory names
    CAMPAIGN_DIR,
    CAMPAIGN_FILE,
    STATUS_FILE,
    # Archive paths
    SET_STUFF_PATH,
    SET_DYNAMIC_CAMPAIGN_PATH,
    SET_MULTIPLAYER_CONQUEST_PATH,
    SET_BREED_MP_PATH,
    ENTITY_PATH,
    PROPERTIES_PATH,
    # File extensions
    DEF_EXTENSION,
    INC_EXTENSION,
    EXT_EXTENSION,
    BAK_EXTENSION,
    BACKUP_PATTERN,
    # File operations
    READ_MODE,
    WRITE_MODE,
    # Campaign data patterns
    CAMPAIGN_SQUADS_MARKER,
    DECEASED_MEMBER_ID,
    INVENTORY_PREFIX,
    ENTITY_MARKER,
    HUMAN_MARKER,
    ITEM_MARKER,
    TAB_CLOSE,
    # Regex patterns
    SQUAD_INFO_PATTERN,
    INVENTORY_SECTION_PATTERN,
    SUPPLIES_PATTERN,
    RESOURCES_PATTERN,
    FUEL_PATTERN,
    CAMPAIGN_SQUADS_PATTERN,
    SAVE_SQUADS_PATTERN,
    USER_PLAYER_PATTERN,
    MP_STATUS_PATTERN,
    AP_STATUS_PATTERN,
    HUMAN_RESOURCES_PATTERN,
    ENTITY_SUPPLIES_PATTERN,
    ENTITY_FUEL_PATTERN,
    # Replacement templates
    CURRENT_VALUE_REPLACEMENT,
    MP_VALUE_REPLACEMENT,
    AP_VALUE_REPLACEMENT,
    SECTION_REPLACEMENT,
    # Logging messages
    EXTRACTED_MESSAGE,
    ALREADY_EXISTS_MESSAGE,
    OVERWRITING_MESSAGE,
    BACKUP_EXISTS_MESSAGE,
    STATUS_BACKUP_EXISTS_MESSAGE,
    BACKUP_CREATED_MESSAGE,
    STATUS_BACKUP_CREATED_MESSAGE,
    STATUS_SAVED_MESSAGE,
    SQUADS_SAVED_MESSAGE,
    UNITS_SAVED_MESSAGE,
    ARCHIVE_CREATED_MESSAGE,
    ADDED_TO_ARCHIVE_MESSAGE,
    ERROR_SAVING_MESSAGE,
    ERROR_CREATING_ARCHIVE_MESSAGE,
    # Other constants
    RESUPPLY_FILENAME,
    QUOTE_CHAR,
    NEWLINE,
    TAB,
    ANIMATION_KEYWORD,
    CURLY_BRACES,
    NEWLINE_JOIN,
    EMPTY_JOIN,
    TAB_TAB_FORMAT,
    TAB_FORMAT,
    CAMPAIGN_SQUADS_FORMAT,
)

VEHICLES_EXCLUDED_ELEMENTS = [
    "/placeholder",
    "/generic/car",
    "/generic/marine",
    "/generic/train",
    "/x/",
    "_x",
    "_xx",
]


class DataManager:
    """Manage campaign data extraction, parsing, and saving operations."""

    def __init__(
        self,
        data_dir_path: Path,
        gamelogic_file_path: Path,
        vehicle_file_path: Path,
        properties_file_path: Path,
        campaign_save_file_path: Path,
        knowledge_base: KnowledgeBase,
        logger: ConsoleLogger,
    ) -> None:
        """Initialize data manager with file paths and dependencies.

        Args:
            data_dir_path (Path): Directory for extracted game data
            gamelogic_file_path (Path): Path to gamelogic archive file
            vehicle_file_path (Path): Path to vehicle data archive
            properties_file_path (Path): Path to properties archive
            campaign_save_file_path (Path): Path to campaign save file
            knowledge_base (KnowledgeBase): Game knowledge database
            logger (ConsoleLogger): Console output logger
        """
        self.data_dir_path = data_dir_path
        self.gamelogic_file_path = gamelogic_file_path
        self.vehicle_file_path = vehicle_file_path
        self.properties_file_path = properties_file_path
        self.campaign_save_file_path = campaign_save_file_path
        self.campaign_data_dir_path = data_dir_path / CAMPAIGN_DIR
        self.campaign_data_file_path = self.campaign_data_dir_path / CAMPAIGN_FILE
        self.campaign_status_file_path = self.campaign_data_dir_path / STATUS_FILE

        self.knowledge_base = knowledge_base

        self.logger = logger

        self.extract_set_stuff_from_game_data()
        self.extract_set_breed_from_game_data()
        self.extract_vehicles_from_game_data()
        self.extract_properties_from_game_data()
        self.extract_set_dynamic_campaign_from_game_data()
        self.extract_set_multiplayer_units_conquest_from_game_data()
        self.extract_campaign_files()

    def extract_set_stuff_from_game_data(self) -> None:
        """Extract set/stuff data from gamelogic archive."""
        set_stuff_path = self.data_dir_path / SET_STUFF_PATH
        if not os.path.exists(set_stuff_path):
            with zipfile.ZipFile(self.gamelogic_file_path) as archive:
                for file in archive.namelist():
                    if file.startswith(SET_STUFF_PATH + "/"):
                        archive.extract(file, self.data_dir_path)
                self.logger.log(
                    EXTRACTED_MESSAGE.format(SET_STUFF_PATH + "/", set_stuff_path)
                )

        else:
            self.logger.log(
                ALREADY_EXISTS_MESSAGE.format(SET_STUFF_PATH + "/", set_stuff_path)
            )

    def extract_set_dynamic_campaign_from_game_data(self) -> None:
        """Extract set/dynamic_campaign data from gamelogic archive."""
        set_dynamic_campaign_path = self.data_dir_path / SET_DYNAMIC_CAMPAIGN_PATH
        if not os.path.exists(set_dynamic_campaign_path):
            with zipfile.ZipFile(self.gamelogic_file_path) as archive:
                for file in archive.namelist():
                    if file.startswith(SET_DYNAMIC_CAMPAIGN_PATH + "/"):
                        archive.extract(file, self.data_dir_path)
                self.logger.log(
                    EXTRACTED_MESSAGE.format(
                        SET_DYNAMIC_CAMPAIGN_PATH + "/", set_dynamic_campaign_path
                    )
                )

        else:
            self.logger.log(
                ALREADY_EXISTS_MESSAGE.format(
                    SET_DYNAMIC_CAMPAIGN_PATH + "/", set_dynamic_campaign_path
                )
            )

    def extract_set_multiplayer_units_conquest_from_game_data(self) -> None:
        """Extract set/multiplayer/units/conquest data from gamelogic archive."""
        set_mp_units_conquest_path = self.data_dir_path / SET_MULTIPLAYER_CONQUEST_PATH
        if not os.path.exists(set_mp_units_conquest_path):
            with zipfile.ZipFile(self.gamelogic_file_path) as archive:
                for file in archive.namelist():
                    if file.startswith(SET_MULTIPLAYER_CONQUEST_PATH + "/"):
                        archive.extract(file, self.data_dir_path)
                self.logger.log(
                    EXTRACTED_MESSAGE.format(
                        SET_MULTIPLAYER_CONQUEST_PATH + "/", set_mp_units_conquest_path
                    )
                )

        else:
            self.logger.log(
                ALREADY_EXISTS_MESSAGE.format(
                    SET_MULTIPLAYER_CONQUEST_PATH + "/", set_mp_units_conquest_path
                )
            )

    def extract_campaign_files(self) -> None:
        """Extract campaign files from save archive to working directory."""
        if os.path.exists(self.campaign_data_file_path):
            self.logger.log(OVERWRITING_MESSAGE.format(self.campaign_data_dir_path))
        with zipfile.ZipFile(self.campaign_save_file_path, READ_MODE) as save_file:
            save_file.extractall(self.campaign_data_dir_path)
            self.logger.log(
                EXTRACTED_MESSAGE.format("campaign files", self.campaign_data_dir_path)
            )

    def extract_set_breed_from_game_data(self) -> None:
        """Extract set/breed/mp data from gamelogic archive."""
        set_breed_path = self.data_dir_path / SET_BREED_MP_PATH
        if not os.path.exists(set_breed_path):
            with zipfile.ZipFile(self.gamelogic_file_path) as archive:
                for file in archive.namelist():
                    if file.startswith(SET_BREED_MP_PATH):
                        archive.extract(file, self.data_dir_path)
                self.logger.log(
                    EXTRACTED_MESSAGE.format(SET_BREED_MP_PATH, set_breed_path)
                )

        else:
            self.logger.log(
                ALREADY_EXISTS_MESSAGE.format(SET_BREED_MP_PATH, set_breed_path)
            )

    def extract_squads_information(
        self, keep_deceased_members: bool = False
    ) -> tuple[list[SquadInfo], list[str]]:
        """Extract squad information from campaign data file.

        Args:
            keep_deceased_members (bool): Whether to include deceased squad members

        Returns:
            tuple[list[SquadInfo], list[str]]: Squad info objects and raw entries
        """
        squads = []
        squads_entries = []
        with open(self.campaign_data_file_path, READ_MODE) as file:
            for line in file:
                if CAMPAIGN_SQUADS_MARKER in line:
                    squad_id_counter = 0
                    for subline in file:
                        match = re.search(SQUAD_INFO_PATTERN, subline)
                        if match:
                            squad_info = match.group(0)

                            squads_entries.append(squad_info)

                            squad_info = squad_info.strip(CURLY_BRACES)
                            squad_info_split = squad_info.split()
                            squad_members = [
                                squad_member_id
                                for squad_member_id in squad_info_split[2:]
                            ]

                            if not keep_deceased_members:
                                squad_members = [
                                    squad_member_id
                                    for squad_member_id in squad_members
                                    if squad_member_id != DECEASED_MEMBER_ID
                                ]

                            squad_info_dict = SquadInfo(
                                squad_id=squad_id_counter,
                                squad_name=squad_info_split[0],
                                stage=squad_info_split[1],
                                squad_members=squad_members,
                            )
                            squads.append(squad_info_dict)
                            squad_id_counter += 1
                        else:
                            break
                    break
        return squads, squads_entries

    def extract_squad_member_inventory(
        self, squad_id: int, squad_member_id: str, squad_member_breed: str
    ) -> EntityInventory:
        """Extract inventory data for a specific squad member.

        Args:
            squad_id (int): ID of the squad
            squad_member_id (str): Hex ID of the squad member
            squad_member_breed (str): Breed type of the squad member

        Returns:
            EntityInventory: Complete inventory data for the member
        """
        inventory_entries = []
        object_properties_entry = ""
        with open(self.campaign_data_file_path, READ_MODE) as file:
            for line in file:
                if squad_member_id in line and (
                    ENTITY_MARKER in line or HUMAN_MARKER in line
                ):
                    for subline in file:
                        object_properties_entry += subline
                        if subline == TAB_CLOSE:
                            break

                if f"{INVENTORY_PREFIX}{squad_member_id}" in line:
                    for subline in file:
                        if ITEM_MARKER in subline:
                            inventory_entries.append(subline)
                        if subline == TAB_CLOSE:
                            break
                    break

        supplies_match = re.search(SUPPLIES_PATTERN, object_properties_entry)
        supplies = int(supplies_match.group(1)) if supplies_match else -1

        resources_match = re.search(RESOURCES_PATTERN, object_properties_entry)
        resources = int(resources_match.group(1)) if resources_match else -1

        fuel_match = re.search(FUEL_PATTERN, object_properties_entry)
        fuel = float(fuel_match.group(1)) if fuel_match else -1.0

        return EntityInventory(
            squad_id=squad_id,
            entity_id=squad_member_id,
            entity_breed=squad_member_breed,
            inventory_entries=inventory_entries,
            supplies=supplies,
            resources=resources,
            fuel=fuel,
            knowledge_base=self.knowledge_base,
        )

    def extract_squad_member_breed(self, squad_member_id: str) -> str:
        """Extract breed type for a specific squad member.

        Args:
            squad_member_id (str): Hex ID of the squad member

        Returns:
            str: Breed type of the squad member
        """
        with open(self.campaign_data_file_path, READ_MODE) as file:
            for line in file:
                if squad_member_id in line:
                    if f"{HUMAN_MARKER}" in line or f"{ENTITY_MARKER}" in line:
                        line_split = line.split()
                        breed = line_split[1].strip(QUOTE_CHAR)
                        break

        return breed

    def extract_vehicles_from_game_data(self) -> None:
        """Extract vehicle entity data from vehicle archive."""
        entity_vehicle_path = self.data_dir_path / ENTITY_PATH
        if not os.path.exists(entity_vehicle_path):
            with zipfile.ZipFile(self.vehicle_file_path) as archive:
                for file in archive.namelist():
                    if any(
                        [
                            excluded_elem in file
                            for excluded_elem in VEHICLES_EXCLUDED_ELEMENTS
                        ]
                    ):
                        continue

                    if (DEF_EXTENSION not in file) and (INC_EXTENSION not in file):
                        continue

                    archive.extract(file, entity_vehicle_path)
                self.logger.log(
                    EXTRACTED_MESSAGE.format("entity/-vehicles/", entity_vehicle_path)
                )

        else:
            self.logger.log(
                ALREADY_EXISTS_MESSAGE.format("entity/-vehicles/", entity_vehicle_path)
            )

    def extract_properties_from_game_data(self) -> None:
        """Extract properties data from properties archive."""
        properties_path = self.data_dir_path / PROPERTIES_PATH
        if not os.path.exists(properties_path):
            with zipfile.ZipFile(self.properties_file_path) as archive:
                for file in archive.namelist():
                    if ANIMATION_KEYWORD in file:
                        continue
                    if RESUPPLY_FILENAME in file:
                        archive.extract(file, self.data_dir_path)
                        continue
                    if EXT_EXTENSION not in file:
                        continue

                    archive.extract(file, self.data_dir_path)
                self.logger.log(
                    EXTRACTED_MESSAGE.format(PROPERTIES_PATH + "/", self.data_dir_path)
                )

        else:
            self.logger.log(
                ALREADY_EXISTS_MESSAGE.format(PROPERTIES_PATH + "/", self.data_dir_path)
            )

    def create_campaign_file_backup(self) -> None:
        """Create backup copy of campaign data file."""
        campaign_data_backup_path = self.campaign_data_file_path.with_suffix(
            BAK_EXTENSION
        )
        if campaign_data_backup_path.exists():
            self.logger.log(BACKUP_EXISTS_MESSAGE.format(campaign_data_backup_path))
        with open(self.campaign_data_file_path, READ_MODE) as original_file:
            content = original_file.read()
        with open(campaign_data_backup_path, WRITE_MODE) as backup_file:
            backup_file.write(content)

        self.logger.log(BACKUP_CREATED_MESSAGE.format(campaign_data_backup_path))

    def create_campaign_status_file_backup(self) -> None:
        """Create backup copy of campaign status file."""
        campaign_status_backup_path = self.campaign_status_file_path.with_suffix(
            BAK_EXTENSION
        )
        if campaign_status_backup_path.exists():
            self.logger.log(
                STATUS_BACKUP_EXISTS_MESSAGE.format(campaign_status_backup_path)
            )
        with open(self.campaign_status_file_path, READ_MODE) as original_file:
            content = original_file.read()
        with open(campaign_status_backup_path, WRITE_MODE) as backup_file:
            backup_file.write(content)

        self.logger.log(
            STATUS_BACKUP_CREATED_MESSAGE.format(campaign_status_backup_path)
        )

    def save_squad_member_inventory(self, entity_inventory: EntityInventory) -> None:
        """Save updated squad member inventory to campaign file.

        Args:
            entity_inventory (EntityInventory): Complete inventory data to save
        """
        entity_id = entity_inventory.entity_id
        inventory_entry_str = entity_inventory.prepare_inventory_for_saving()
        with open(self.campaign_data_file_path, READ_MODE) as file:
            content = file.read()

        updated_content = self.replace_inventory_section(
            content, entity_id, inventory_entry_str
        )

        if entity_inventory.resources >= 0:
            updated_content = self.replace_supplies_resources_section(
                updated_content, entity_inventory
            )
        if entity_inventory.supplies >= 0:
            updated_content = self.replace_supplies_section(
                updated_content, entity_inventory
            )
        if entity_inventory.fuel >= 0:
            updated_content = self.replace_fuel_section(
                updated_content, entity_inventory
            )

        with open(self.campaign_data_file_path, WRITE_MODE) as file:
            file.write(updated_content)

    def replace_inventory_section(
        self, content: str, inventory_id: str, replacement: str
    ) -> str:
        """Replace inventory section in campaign file by entity ID.

        Args:
            content (str): Full campaign file content
            inventory_id (str): Hex ID of inventory to replace
            replacement (str): New inventory content to insert

        Returns:
            str: Updated file content with replacement
        """

        if f"{INVENTORY_PREFIX}{inventory_id}" not in content:
            result = self.add_inventory_section(content, replacement)
        else:
            # Pattern to match the entire inventory block with the specified ID
            pattern = INVENTORY_SECTION_PATTERN.format(inventory_id)

            # Replace the matched section with the new content
            result = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return result

    def replace_supplies_resources_section(
        self, content: str, entity_inventory: EntityInventory
    ) -> str:
        """Replace resources value in entity extender section.

        Args:
            content (str): Full campaign file content
            entity_inventory (EntityInventory): Inventory with new resources value

        Returns:
            str: Updated content with new resources value
        """
        escaped_type = re.escape(entity_inventory.entity_breed)
        escaped_id = re.escape(entity_inventory.entity_id)

        # Pattern that captures everything before and after the current value
        pattern = HUMAN_RESOURCES_PATTERN.format(
            escaped_type=escaped_type, escaped_id=escaped_id
        )

        # Replacement with new current value
        replacement = CURRENT_VALUE_REPLACEMENT.format(entity_inventory.resources)

        # Perform the replacement
        updated_content = re.sub(pattern, replacement, content)

        return updated_content

    def replace_supplies_section(
        self, content: str, entity_inventory: EntityInventory
    ) -> str:
        """Replace supplies value in entity supply zone section.

        Args:
            content (str): Full campaign file content
            entity_inventory (EntityInventory): Inventory with new supplies value

        Returns:
            str: Updated content with new supplies value
        """
        escaped_type = re.escape(entity_inventory.entity_breed)
        escaped_id = re.escape(entity_inventory.entity_id)

        # Pattern to find and replace the supply_zone current value within the specific Entity block
        pattern = ENTITY_SUPPLIES_PATTERN.format(
            escaped_type=escaped_type, escaped_id=escaped_id
        )

        # Replacement with new current value
        replacement = CURRENT_VALUE_REPLACEMENT.format(entity_inventory.supplies)

        # Perform the replacement
        updated_content = re.sub(pattern, replacement, content)

        return updated_content

    def replace_fuel_section(
        self, content: str, entity_inventory: EntityInventory
    ) -> str:
        """Replace fuel value in entity fuel bag section.

        Args:
            content (str): Full campaign file content
            entity_inventory (EntityInventory): Inventory with new fuel value

        Returns:
            str: Updated content with new fuel value
        """
        escaped_type = re.escape(entity_inventory.entity_breed)
        escaped_id = re.escape(entity_inventory.entity_id)

        # Pattern to find and replace the FuelBag Remain value within the specific Entity block
        pattern = ENTITY_FUEL_PATTERN.format(
            escaped_type=escaped_type, escaped_id=escaped_id
        )

        # Replacement with new remain value
        replacement = CURRENT_VALUE_REPLACEMENT.format(entity_inventory.fuel)

        # Perform the replacement
        updated_content = re.sub(pattern, replacement, content)

        return updated_content

    def add_inventory_section(self, content: str, inventory_section: str) -> str:
        """Add new inventory section to campaign file.

        Args:
            content (str): Full campaign file content
            inventory_section (str): New inventory section to add

        Returns:
            str: Updated content with new inventory section
        """
        # Prepare the pattern - find the section marker at the start of a line
        pattern = CAMPAIGN_SQUADS_PATTERN

        # Replace with the new content followed by the section marker
        modified_content = re.sub(
            pattern, SECTION_REPLACEMENT.format(inventory_section), content
        )
        return modified_content

    def save_new_squad_members(
        self, squads_entries: list[str], new_unit_entries: list[str]
    ) -> None:
        """Save new squad members and unit entries to campaign file.

        Args:
            squads_entries (list[str]): Updated squad entries
            new_unit_entries (list[str]): New unit entries to add
        """
        squads_entries_str = self.prepare_squads_entries_for_saving(squads_entries)
        self.save_squads_entries(squads_entries_str)
        new_unit_entries_str = self.prepare_new_unit_entries_for_saving(
            new_unit_entries
        )
        self.save_new_unit_entries(new_unit_entries_str)

    def prepare_squads_entries_for_saving(self, squads_entries: list[str]) -> str:
        """Format squad entries for saving to campaign file.

        Args:
            squads_entries (list[str]): Raw squad entries

        Returns:
            str: Formatted squad entries string
        """
        squads_entries = [TAB_TAB_FORMAT.format(entry) for entry in squads_entries]
        squads_entries_str = NEWLINE_JOIN.join(squads_entries)
        squads_entries_str = CAMPAIGN_SQUADS_FORMAT.format(squads_entries_str)

        return squads_entries_str

    def prepare_new_unit_entries_for_saving(self, new_unit_entries: list[str]) -> str:
        """Format new unit entries for saving to campaign file.

        Args:
            new_unit_entries (list[str]): Raw unit entries

        Returns:
            str: Formatted unit entries string
        """
        new_unit_entries = [TAB_FORMAT.format(entry) for entry in new_unit_entries]
        new_unit_entries_str = EMPTY_JOIN.join(new_unit_entries)

        return new_unit_entries_str

    def save_squads_entries(self, squads_entries_str: str) -> None:
        """Save squad entries to campaign file.

        Args:
            squads_entries_str (str): Formatted squad entries to save
        """
        with open(self.campaign_data_file_path, READ_MODE) as file:
            content = file.read()

        # Replace the existing CampaignSquads section with the new one
        updated_content = re.sub(
            SAVE_SQUADS_PATTERN,
            f"{squads_entries_str}",
            content,
            flags=re.DOTALL,
        )

        with open(self.campaign_data_file_path, WRITE_MODE) as file:
            file.write(updated_content)

        self.logger.log(SQUADS_SAVED_MESSAGE.format(self.campaign_data_file_path))

    def save_new_unit_entries(self, new_unit_entries_str: str) -> None:
        """Save new unit entries to campaign file.

        Args:
            new_unit_entries_str (str): Formatted unit entries to save
        """
        with open(self.campaign_data_file_path, READ_MODE) as file:
            content = file.read()
        updated_content = re.sub(
            USER_PLAYER_PATTERN,
            f"{new_unit_entries_str}\\1",
            content,
            count=1,  # Only replace first occurrence
        )
        with open(self.campaign_data_file_path, WRITE_MODE) as file:
            file.write(updated_content)

        self.logger.log(UNITS_SAVED_MESSAGE.format(self.campaign_data_file_path))

    def save_campaign_status_info(self) -> None:
        """Save campaign status information (MP and AP values) to status file."""
        with open(self.campaign_status_file_path, READ_MODE) as file:
            content = file.read()

            replacement = MP_VALUE_REPLACEMENT.format(
                round(self.knowledge_base.campaign_status_info.mp, 2)
            )
            updated_content = re.sub(MP_STATUS_PATTERN, replacement, content, 1)

            replacement = AP_VALUE_REPLACEMENT.format(
                round(self.knowledge_base.campaign_status_info.ap, 2)
            )
            updated_content = re.sub(AP_STATUS_PATTERN, replacement, updated_content, 1)

        with open(self.campaign_status_file_path, WRITE_MODE) as file:
            file.write(updated_content)

        self.logger.log(STATUS_SAVED_MESSAGE.format(self.campaign_status_file_path))

    def save_campaign_file(self) -> None:
        """Save campaign file after modifications by creating archive."""
        try:
            # Use the general archive method to save all files in campaign directory
            self.create_archive_from_directory(
                source_directory=self.campaign_data_dir_path,
                archive_path=self.campaign_save_file_path,
                exclude_patterns=[BAK_EXTENSION],  # Exclude backup files
                preserve_structure=False,  # Keep flat structure like original
            )
        except Exception as e:
            self.logger.log(ERROR_SAVING_MESSAGE.format(str(e)))

    def create_archive_from_directory(
        self,
        source_directory: Path,
        archive_path: Path,
        include_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
        preserve_structure: bool = True,
    ) -> None:
        """Create ZIP archive from directory with filtering options.

        Args:
            source_directory (Path): Directory to archive
            archive_path (Path): Output ZIP file path
            include_patterns (list[str]): Glob patterns for files to include
            exclude_patterns (list[str]): Glob patterns for files to exclude
            preserve_structure (bool): Whether to preserve directory structure
        """
        try:
            with zipfile.ZipFile(
                str(archive_path), WRITE_MODE, zipfile.ZIP_DEFLATED
            ) as zip_file:
                files_added = 0

                # Get all files in directory and subdirectories
                all_files = list(source_directory.rglob("*"))

                for file_path in all_files:
                    if not file_path.is_file():
                        continue

                    # Check include patterns
                    if include_patterns:
                        if not any(
                            file_path.match(pattern) for pattern in include_patterns
                        ):
                            continue

                    # Check exclude patterns
                    if exclude_patterns:
                        if any(
                            file_path.match(pattern) for pattern in exclude_patterns
                        ):
                            continue

                    # Determine archive name
                    if preserve_structure:
                        arcname = file_path.relative_to(source_directory)
                    else:
                        arcname = file_path.name

                    zip_file.write(str(file_path), arcname=str(arcname))
                    files_added += 1
                    self.logger.log(ADDED_TO_ARCHIVE_MESSAGE.format(arcname))

                self.logger.log(
                    ARCHIVE_CREATED_MESSAGE.format(archive_path, files_added)
                )

        except Exception as e:
            self.logger.log(ERROR_CREATING_ARCHIVE_MESSAGE.format(str(e)))
