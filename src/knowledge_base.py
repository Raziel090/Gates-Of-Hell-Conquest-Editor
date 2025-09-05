"""Game knowledge database for items, weapons, breeds, and game mechanics."""

from dataclasses import dataclass
import glob
import math
import os
from pathlib import Path
import re

import numpy as np

from src.console_logger import ConsoleLogger
from src.constants import (
    # File extensions and patterns
    EXCLUDED_FILES_EXTENSIONS,
    EXCLUDED_PATTERNS,
    # Archive and game data paths
    SET_STUFF_PATH,
    SET_BREED_PATH,
    ENTITY_VEHICLE_PATH,
    PROPERTIES_PATH,
    SET_MULTIPLAYER_CONQUEST_PATH,
    CAMPAIGN_DIR,
    STATUS_FILE,
    # Keywords
    MASS_KEYWORD,
    WEAPONRY_KEYWORD,
    WEAPON_KEYWORD,
)


@dataclass
class BreedItemInfo:
    """Store breed item information with visibility and amount."""

    game_item_name: str
    amount: int
    is_visible: bool = True


@dataclass
class WeaponInfo:
    """Store weapon information including name and type."""

    weapon_name: str
    weapon_type: str


@dataclass
class SquadCompositionInfo:
    """Store squad composition details for multiplayer units."""

    name: str
    side: str
    period: str
    cost: int
    members: dict[str, int]


@dataclass
class CampaignStatusInfo:
    """Store campaign status values including points and army."""

    mp: float
    sp: float
    ap: float
    rp: float
    army: str


class KnowledgeBase:
    """Central knowledge database for game items, weapons, breeds, and mechanics."""

    def __init__(
        self,
        data_dir_path: Path,
        gamelogic_file_path: Path,
        logger: ConsoleLogger,
    ) -> None:
        """Initialize knowledge base with game data paths and logger.

        Args:
            data_dir_path (Path): Path to extracted game data directory
            gamelogic_file_path (Path): Path to gamelogic archive file
            logger (ConsoleLogger): Console output logger
        """
        self.data_dir_path = data_dir_path
        self.gamelogic_file_path = gamelogic_file_path
        self.game_items_path = self.data_dir_path / SET_STUFF_PATH
        self.game_breeds_path = self.data_dir_path / SET_BREED_PATH
        self.game_vehicles_path = self.data_dir_path / ENTITY_VEHICLE_PATH
        self.game_properties_path = self.data_dir_path / PROPERTIES_PATH
        self.game_conquest_units_path = (
            self.data_dir_path / SET_MULTIPLAYER_CONQUEST_PATH
        )
        self.campaign_status_file_path = self.data_dir_path / CAMPAIGN_DIR / STATUS_FILE

        self.logger = logger

        self.item_pattern_sizes = {}
        self.item_sizes = {}
        self.item_block_sizes = {}
        self.breeds_inventories: dict[str, BreedItemInfo] = {}
        self.vehicle_inventories: dict[str, BreedItemInfo] = {}
        self.weapons_info_list: list[WeaponInfo] = []
        self.weapons_list: list[str] = []
        self.vehicles_properties_lists: dict[str, list[str]] = {}
        self.vehicles_properties: dict[str, str] = {}
        self.vehicles_fuel_properties: dict[str, int] = {}
        self.properties_inventory_sizes: dict[str, dict] = {}
        self.properties_inventory_entries: dict[str, list[str]] = {}
        self.squad_compositions: dict[str, SquadCompositionInfo] = {}
        self.infantry_costs: dict[str, float] = {}
        self.vehicles_costs: dict[str, float] = {}
        self.campaign_status_info: CampaignStatusInfo = None
        self.item_weights: dict[str, dict] = {}

    def init_knowledge_base(self) -> None:
        """Initialize all knowledge base components by loading game data."""
        self.get_item_inventory_size_information()
        self.get_breeds_inventory_information()
        self.get_vehicle_properties()
        self.get_inventory_information_from_properties()
        self.get_vehicles_inventory_information()
        self.get_weapons_list()
        self.create_vehicles_properties()
        self.get_infantry_costs()
        self.get_squads_compositions()
        self.get_campaign_status_information()
        self.get_item_weights()

    def get_item_files_paths(self) -> list[str]:
        """Get all item file paths from game data directory.

        Returns:
            list[str]: List of item file paths excluding directories and excluded extensions
        """
        item_files_paths = glob.glob(
            f"{str(self.game_items_path)}/**/*", recursive=True
        )
        item_files_paths = [
            file_path for file_path in item_files_paths if not os.path.isdir(file_path)
        ]

        for excluded_file in EXCLUDED_FILES_EXTENSIONS:
            item_files_paths = [
                file_path
                for file_path in item_files_paths
                if not excluded_file in file_path
            ]

        item_files_paths = list(set(item_files_paths))

        return item_files_paths

    def get_item_pattern_sizes(self, item_pattern_files_paths: list[str]) -> dict:
        """Extract item pattern sizes from pattern files.

        Args:
            item_pattern_files_paths (list[str]): List of pattern file paths

        Returns:
            dict: Dictionary mapping pattern names to size information
        """
        for file_path in item_pattern_files_paths:
            pattern_name = file_path.split("\\")[-1]

            with open(file_path, "r") as f:
                content = f.read()

                if "{inventory" in content:
                    if size_match := re.search(r"\{size (\d+) (\d+)\s*\}", content):
                        self.item_pattern_sizes[pattern_name] = {
                            "x": size_match.group(1),
                            "y": size_match.group(2),
                        }
                    continue

                if from_match := re.search(r"\{from\s+\"(.*?)\"", content):
                    if "throwable" in from_match.group(1):
                        continue

                    pattern = ".".join(reversed(from_match.group(1).split()))
                    self.item_pattern_sizes[pattern_name] = {"pattern_to_seek": pattern}
                else:
                    self.item_pattern_sizes[pattern_name] = {"x": "0", "y": "0"}

        # Resolve pattern references
        return {
            k: self._resolve_pattern_size(v) for k, v in self.item_pattern_sizes.items()
        }

    def _resolve_pattern_size(self, pattern_data: dict) -> dict:
        """Recursively resolve pattern size references.

        Args:
            pattern_data (dict): Pattern data that may contain references

        Returns:
            dict: Resolved pattern size with x and y dimensions
        """
        if "pattern_to_seek" not in pattern_data:
            return pattern_data

        target = self.item_pattern_sizes.get(pattern_data["pattern_to_seek"])
        if not target:
            return {"x": "0", "y": "0"}

        return (
            self._resolve_pattern_size(target)
            if "pattern_to_seek" in target
            else target
        )

    def get_item_sizes(self, item_files_paths: list[str]) -> dict:
        """Extract item sizes from item definition files.

        Args:
            item_files_paths (list[str]): List of item file paths

        Returns:
            dict: Dictionary mapping item names to size information
        """
        for item_file_path in item_files_paths:
            item_name = item_file_path.split("\\")[-1]

            with open(item_file_path, "r") as item_file:
                item_info = item_file.read()

                if any(pattern in item_info for pattern in EXCLUDED_PATTERNS):
                    continue

                if "{inventory" in item_info:
                    if block_match := re.search(r"\{block (\d+)\s*\}", item_info):
                        self.item_block_sizes[item_name] = block_match.group(1)
                    if size_match := re.search(r"\{size (\d+) (\d+)\s*\}", item_info):
                        self.item_sizes[item_name] = {
                            "x": size_match.group(1),
                            "y": size_match.group(2),
                        }
                    elif "special" in item_file_path:
                        self.item_sizes[item_name] = {"x": "2", "y": "2"}
                    else:
                        self.logger.log(f"No size in: {item_info}")
                    continue

                if from_match := re.search(r"\{from\s+\"(.*?)\"", item_info):
                    pattern = from_match.group(1)

                    if "\\gun\\" in item_file_path or "\\reactive\\" in item_file_path:
                        self.item_sizes[item_name] = {"x": "0", "y": "0"}
                        continue

                    pattern_to_seek = self.create_correct_pattern_to_seek(pattern)

                    if "pattern" in pattern:
                        self.item_sizes[item_name] = self.item_pattern_sizes[
                            pattern_to_seek
                        ]
                    else:
                        self.item_sizes[item_name] = {
                            "pattern_to_seek": pattern_to_seek
                        }
                else:
                    # self.logger.log(f"Unrecognized item: {item_file_path}")
                    continue

        updated_item_sizes = {}
        for k, v in self.item_sizes.items():
            if "pattern_to_seek" not in v:
                updated_item_sizes[k] = v
                continue

            pattern = v["pattern_to_seek"]
            current_sizes = self.item_sizes.get(pattern) or self.item_sizes.get(
                f"{pattern}.weapon"
            )
            updated_item_sizes[k] = current_sizes

        return updated_item_sizes

    def create_correct_pattern_to_seek(self, pattern: str) -> str:
        """Create correct pattern name for item pattern lookup.

        Args:
            pattern (str): Raw pattern string from item definition

        Returns:
            str: Formatted pattern name for lookup
        """
        pattern_parts = pattern.split()
        if "knife" in pattern:
            return ".".join(pattern_parts)
        if "usa_grenade" in pattern:
            return f"{pattern_parts[0]}.{pattern_parts[2]}.{pattern_parts[1]}"
        return ".".join(reversed(pattern_parts))

    def handle_exceptions_for_block_sizes(self, item_files_paths: list[str]) -> dict:
        """Handle special cases for item block sizes.

        Args:
            item_files_paths (list[str]): List of item file paths

        Returns:
            dict: Dictionary mapping item names to block sizes for special cases
        """
        item_block_sizes = {}
        for item_file_path in item_files_paths:
            if "rifle\\grenade\\" in item_file_path and ".ammo" in item_file_path:
                item_name = item_file_path.split("\\")[-1]
                item_block_sizes[item_name] = "5"
            if "\\smoke grenade\\nbks.grenade" in item_file_path:
                item_name = item_file_path.split("\\")[-1]
                item_block_sizes[item_name] = "10"

        return item_block_sizes

    def get_item_inventory_size_information(self) -> None:
        """Load and process all item inventory size information."""
        assert self.game_items_path.exists(), "Game items path does not exist!"
        item_files_paths = self.get_item_files_paths()
        item_pattern_files_paths = [
            item_file_path
            for item_file_path in item_files_paths
            if ".pattern" in item_file_path
        ]
        item_files_paths = [
            item_file_path
            for item_file_path in item_files_paths
            if item_file_path not in item_pattern_files_paths
        ]

        self.item_pattern_sizes = self.get_item_pattern_sizes(item_pattern_files_paths)
        assert self.item_pattern_sizes != {}

        self.item_sizes = self.get_item_sizes(item_files_paths)
        assert self.item_sizes != {}

        block_sizes = self.handle_exceptions_for_block_sizes(item_files_paths)
        self.item_block_sizes.update(block_sizes)
        assert self.item_block_sizes != {}

    def get_breed_files_paths(self) -> list[str]:
        """Get all breed file paths from game data directory.

        Returns:
            list[str]: List of breed file paths excluding directories and excluded extensions
        """
        breed_files_paths = glob.glob(
            f"{str(self.game_breeds_path)}/**/*", recursive=True
        )
        breed_files_paths = [
            file_path for file_path in breed_files_paths if not os.path.isdir(file_path)
        ]

        for excluded_file in EXCLUDED_FILES_EXTENSIONS:
            breed_files_paths = [
                file_path
                for file_path in breed_files_paths
                if not excluded_file in file_path
            ]

        breed_files_paths = list(set(breed_files_paths))

        return breed_files_paths

    def get_breeds_inventory_entries(self, breed_files_paths: list[str]) -> dict:
        """Extract inventory entries from breed definition files.

        Args:
            breed_files_paths (list[str]): List of breed file paths

        Returns:
            dict: Dictionary mapping breed names to inventory entries
        """
        breeds_inventory_entries = {}
        for file_path in breed_files_paths:
            with open(file_path, "r") as file:
                current_breed_inventory_entries = []
                for line in file:
                    if f"{{inventory" in line:
                        for subline in file:
                            if "{item" in subline and ";{item" not in subline:
                                current_breed_inventory_entries.append(subline)
                            if subline == "\t}\n":
                                break
                        break
                if not current_breed_inventory_entries:
                    self.logger.log(
                        f"File {file_path} does not contain inventory information"
                    )

                breed_name_split = file_path.split("\\")[-4:]
                breed_name = "/".join(breed_name_split)
                breed_name = re.sub(".set", "", breed_name)

                breeds_inventory_entries[breed_name] = current_breed_inventory_entries
        return breeds_inventory_entries

    def get_correct_item_name(self, item_name: str) -> str:
        """Convert raw item name to correct format for lookup.

        Args:
            item_name (str): Raw item name from game files

        Returns:
            str: Correctly formatted item name
        """
        item_name_parts = item_name.split()
        if "usa_grenade" in item_name:
            return f"{item_name_parts[0]}.{item_name_parts[2]}.{item_name_parts[1]}"
        if "mgun_" in item_name:
            if item_name_parts[0] == "ammo":
                if "mgun_usa" == item_name_parts[1] and "belt" not in item_name:
                    return item_name_parts[1] + f".belt.{item_name_parts[0]}"
                return ".".join(item_name_parts[1:]) + f".{item_name_parts[0]}"
            elif "ammo" not in item_name_parts:
                return ".".join(item_name_parts) + ".ammo"
        if "bullet" in item_name:
            if item_name_parts[0] == "ammo":
                return ".".join(item_name_parts[1:]) + f".{item_name_parts[0]}"
            elif "ammo" not in item_name_parts:
                return ".".join(item_name_parts) + ".ammo"

        if item_name_parts[0] == "ammo":
            return ".".join(item_name_parts[1:]) + f".{item_name_parts[0]}"
        if item_name_parts[0] == "weapon":
            return ".".join(item_name_parts[1:]) + f".{item_name_parts[0]}"
        if "mortar" in item_name:
            if item_name_parts[-1] != "ammo":
                return ".".join(item_name_parts) + ".ammo"

        return ".".join(item_name_parts)

    def convert_breed_inventory_entry_to_game_item_info(
        self, breed_inventory_entry: str
    ) -> BreedItemInfo:
        """Parse breed inventory entry into structured item information.

        Args:
            breed_inventory_entry (str): Raw breed inventory entry string

        Returns:
            BreedItemInfo: Parsed breed item information
        """
        is_visible = True
        whole_pattern = r'\{item\s+"([^"]+)"\s+(\d+\.?\d*)'

        match = re.search(whole_pattern, breed_inventory_entry)
        if match:
            item_name = match.group(1)
            item_name = self.get_correct_item_name(item_name)

            amount = int(np.floor(float(match.group(2))))
            if amount == 0:
                amount = 1
        else:
            item_pattern = r'\{item\s+"([^"]+)"'
            match = re.search(item_pattern, breed_inventory_entry)

            if match:
                item_name = match.group(1)
                item_name = self.get_correct_item_name(item_name)
                amount = 1
            else:
                item_pattern = r'\{weapon\s+"([^"]+)"'
                match = re.search(item_pattern, breed_inventory_entry)
                if match:
                    item_name = match.group(1)
                    item_name = self.get_correct_item_name(item_name)
                    amount = 1
                    is_visible = False
                else:
                    self.logger.log(f"Item name not found in: {breed_inventory_entry}")
                    return None

        return BreedItemInfo(
            game_item_name=item_name, amount=amount, is_visible=is_visible
        )

    def get_breeds_inventory_information(self) -> None:
        """Load and process breed inventory information from game files."""
        assert self.game_breeds_path.exists(), "Game breeds path does not exist!"
        breed_files_paths = self.get_breed_files_paths()

        breeds_inventory_entries = self.get_breeds_inventory_entries(breed_files_paths)

        breed_inventories = {}
        for breed_name, inventory_entries in breeds_inventory_entries.items():
            converted_breed_inventory_entries = []
            for inventory_entry in inventory_entries:
                breed_inventory_entry = (
                    self.convert_breed_inventory_entry_to_game_item_info(
                        inventory_entry
                    )
                )
                if breed_inventory_entry:
                    converted_breed_inventory_entries.append(breed_inventory_entry)
                else:
                    self.logger.log(
                        f"Failed to convert inventory entry: {inventory_entry}"
                    )
            breed_inventories[breed_name] = converted_breed_inventory_entries
        self.breeds_inventories = breed_inventories

    def get_weapons_list(self) -> None:
        """Load and process weapons information from game files."""
        assert self.game_items_path.exists(), "Game items path does not exist!"
        item_files_paths = self.get_item_files_paths()

        item_files_paths = [
            item_file_path
            for item_file_path in item_files_paths
            if not any(pattern in item_file_path for pattern in [".pattern", ".ammo"])
        ]

        item_files_paths = [
            item_file_path
            for item_file_path in item_files_paths
            if any(
                pattern in item_file_path
                for pattern in [
                    "\\bazooka",
                    "\\flame",
                    "\\mgun",
                    "\\pistol",
                    "\\rifle",
                    "\\smg",
                ]
            )
        ]

        weapons_info_list = self.prepare_list_of_weapons(item_files_paths)

        if weapons_info_list:
            weapons_list = [
                weapon_info.weapon_name for weapon_info in weapons_info_list
            ]
            self.weapons_info_list = weapons_info_list
            self.weapons_list = weapons_list
        else:
            self.logger.log("No weapons found in the game data.")

    def prepare_list_of_weapons(self, item_files_paths: list[str]) -> list[WeaponInfo]:
        """Prepare list of weapon information from item files.

        Args:
            item_files_paths: List of item file paths

        Returns:
            list[WeaponInfo]: List of weapon information objects
        """
        weapons_list = []
        for item_file_path in item_files_paths:
            item_file_path_split = item_file_path.split("\\")
            item_name = item_file_path_split[-1]

            item_type = ""
            if item_file_path_split[-2] != "stuff":
                item_type = item_file_path_split[-2]
            if item_file_path_split[-3] != "stuff":
                item_type = f"{item_file_path_split[-3]}\{item_type}"

            with open(item_file_path, "r") as item_file:
                item_info = item_file.read()

                if any(pattern in item_info for pattern in EXCLUDED_PATTERNS):
                    continue

                weapons_list.append(
                    WeaponInfo(
                        weapon_name=item_name,
                        weapon_type=item_type,
                    )
                )

        return weapons_list

    def search_for_breed_with_weapon(self, weapon_name: str) -> list[str]:
        """Search for breeds equipped with specific weapon.

        Args:
            weapon_name: Name of weapon to search for

        Returns:
            list[str]: List of breed names with the weapon
        """
        found_breeds = []
        for breed_name, inventory in self.breeds_inventories.items():
            for item in inventory:
                if item.game_item_name == weapon_name:
                    found_breeds.append(breed_name)
        return found_breeds

    def search_for_vehicle_with_weapon(self, weapon_name: str) -> list[str]:
        """Search for vehicles equipped with specific weapon.

        Args:
            weapon_name: Name of weapon to search for

        Returns:
            list[str]: List of vehicle names with the weapon
        """
        found_vehicles = []
        for vehicle_name, inventory in self.vehicle_inventories.items():
            for item in inventory:
                if item.game_item_name == weapon_name:
                    found_vehicles.append(vehicle_name)
        return found_vehicles

    def search_for_breed_with_item(self, item_name: str) -> list[str]:
        """Search for breeds containing specific item.

        Args:
            item_name: Name of item to search for

        Returns:
            list[str]: List of breed names containing the item
        """
        found_breeds = []
        for breed_name, inventory in self.breeds_inventories.items():
            for item in inventory:
                if item_name in item.game_item_name:
                    found_breeds.append(breed_name)
        return found_breeds

    def find_weapon_in_weapons_info_list(self, weapon_name: str) -> WeaponInfo:
        """Find weapon information by weapon name.

        Args:
            weapon_name: Name of weapon to find

        Returns:
            WeaponInfo: Weapon information or None if not found
        """
        for weapon_info in self.weapons_info_list:
            if weapon_info.weapon_name == weapon_name:
                return weapon_info
        self.logger.log(f"Weapon '{weapon_name}' not found in weapons info list.")
        return None

    def get_vehicle_files_paths(self) -> list[str]:
        """Get paths to all vehicle files.

        Returns:
            list[str]: List of vehicle file paths
        """
        vehicle_files_paths = glob.glob(
            f"{str(self.game_vehicles_path)}/**/*", recursive=True
        )
        vehicle_files_paths = [
            file_path
            for file_path in vehicle_files_paths
            if not os.path.isdir(file_path)
        ]

        vehicle_files_paths = list(set(vehicle_files_paths))

        return vehicle_files_paths

    def get_vehicles_inventory_entries(self, vehicle_files_paths: list[str]) -> dict:
        """Extract inventory entries from vehicle files.

        Args:
            vehicle_files_paths: List of vehicle file paths

        Returns:
            dict: Vehicle inventory entries by vehicle name
        """
        vehicles_inventory_entries = {}
        for file_path in vehicle_files_paths:
            with open(file_path, "r") as file:
                current_vehicle_inventory_entries = []
                for line in file:
                    if f"inventory" in line:
                        for subline in file:
                            if "{item" in subline and ";{item" not in subline:
                                current_vehicle_inventory_entries.append(subline)
                            if subline == "\t}\n":
                                break
                        break

                vehicle_name = file_path.split("\\")[-1]
                vehicle_name = re.sub(r"\.(def)$", "", vehicle_name)

                vehicles_inventory_entries[vehicle_name] = (
                    current_vehicle_inventory_entries
                )
        return vehicles_inventory_entries

    def get_vehicles_invisible_inventory_entries(
        self, vehicle_files_paths: list[str]
    ) -> dict:
        """Extract invisible inventory entries from vehicle files.

        Args:
            vehicle_files_paths: List of vehicle file paths

        Returns:
            dict: Vehicle invisible inventory entries by vehicle name
        """
        vehicles_invisible_inventory_entries = {}
        for file_path in vehicle_files_paths:
            with open(file_path, "r") as file:
                current_vehicle_inventory_entries = []
                for line in file:
                    if f"{{{WEAPONRY_KEYWORD}" in line:
                        for subline in file:
                            if (
                                f"{{{WEAPON_KEYWORD}" in subline
                                and f";{{{WEAPON_KEYWORD}" not in subline
                            ):
                                current_vehicle_inventory_entries.append(subline)
                            if subline == "\t}\n":
                                break
                        break

                vehicle_name = file_path.split("\\")[-1]
                vehicle_name = re.sub(r"\.(def)$", "", vehicle_name)

                vehicles_invisible_inventory_entries[vehicle_name] = list(
                    set(current_vehicle_inventory_entries)
                )
        return vehicles_invisible_inventory_entries

    def get_vehicles_inventories_inclusions(
        self, vehicle_files_paths: list[str]
    ) -> dict[str, str]:
        """Get vehicle inventory inclusions from files.

        Args:
            vehicle_files_paths: List of vehicle file paths

        Returns:
            dict: Vehicle inventory inclusions mapping
        """
        inclusions = {}
        pattern = r'\(include\s+"([^"]+)\.inc"\)'
        for file_path in vehicle_files_paths:
            with open(file_path, "r") as file:
                content = file.read()
                matches = re.findall(pattern, content)
                for match in matches:
                    if "/properties/" in match:
                        continue

                    file_path_split = file_path.split("\\")
                    vehicle_name = file_path_split[-1]
                    vehicle_name = re.sub(".def", "", vehicle_name)
                    inclusions[vehicle_name] = f"{matches[0]}.inc"

        return inclusions

    def get_vehicles_inventory_information(self) -> None:
        assert self.game_vehicles_path.exists(), "Game vehicles path does not exist!"
        vehicle_files_paths = self.get_vehicle_files_paths()

        def_files = [
            file_path for file_path in vehicle_files_paths if ".def" in file_path
        ]

        inc_files = [
            file_path for file_path in vehicle_files_paths if ".inc" in file_path
        ]

        inventories_inclusions = self.get_vehicles_inventories_inclusions(def_files)
        vehicles_inventory_entries = self.get_vehicles_inventory_entries(def_files)
        vehicles_invisible_inventory_entries = (
            self.get_vehicles_invisible_inventory_entries(def_files)
        )
        vehicle_inclusion_inventory_entries = self.get_vehicles_inventory_entries(
            inc_files
        )

        vehicle_inventories: dict[str, list] = {}
        for vehicle_name, inventory_entries in vehicles_inventory_entries.items():
            converted_vehicle_inventory_entries = []
            for inventory_entry in inventory_entries:
                vehicle_inventory_entry = (
                    self.convert_breed_inventory_entry_to_game_item_info(
                        inventory_entry
                    )
                )
                if vehicle_inventory_entry:
                    converted_vehicle_inventory_entries.append(vehicle_inventory_entry)
                else:
                    self.logger.log(
                        f"Failed to convert vehicle inventory entry: {inventory_entry}"
                    )

            vehicle_inventories[vehicle_name] = converted_vehicle_inventory_entries

        for (
            vehicle_name,
            inventory_entries,
        ) in vehicles_invisible_inventory_entries.items():
            converted_vehicle_inventory_entries = []
            for inventory_entry in inventory_entries:
                vehicle_inventory_entry = (
                    self.convert_breed_inventory_entry_to_game_item_info(
                        inventory_entry
                    )
                )
                if vehicle_inventory_entry:
                    converted_vehicle_inventory_entries.append(vehicle_inventory_entry)
                else:
                    self.logger.log(
                        f"Failed to convert vehicle inventory entry: {inventory_entry}"
                    )

            if vehicle_name in vehicle_inventories:
                vehicle_inventories[vehicle_name].extend(
                    converted_vehicle_inventory_entries
                )
            else:
                vehicle_inventories[vehicle_name] = converted_vehicle_inventory_entries

        for (
            vehicle_name,
            inventory_entries,
        ) in vehicle_inclusion_inventory_entries.items():
            converted_vehicle_inventory_entries = []
            for inventory_entry in inventory_entries:
                vehicle_inventory_entry = (
                    self.convert_breed_inventory_entry_to_game_item_info(
                        inventory_entry
                    )
                )
                if vehicle_inventory_entry:
                    converted_vehicle_inventory_entries.append(vehicle_inventory_entry)
                else:
                    self.logger.log(
                        f"Failed to convert vehicle inventory entry: {inventory_entry}"
                    )

            if vehicle_name in vehicle_inventories:
                vehicle_inventories[vehicle_name].extend(
                    converted_vehicle_inventory_entries
                )
            else:
                vehicle_inventories[vehicle_name] = converted_vehicle_inventory_entries

        for vehicle_name, inclusion in inventories_inclusions.items():
            vehicle_inventories[vehicle_name] += vehicle_inventories[inclusion]

        for (
            vehicle_name,
            vehicle_property_types,
        ) in self.vehicles_properties_lists.items():

            for property_name in vehicle_property_types:
                vehicle_property_inventory_entries = self.properties_inventory_entries[
                    property_name
                ]

                for inventory_entry in vehicle_property_inventory_entries:
                    inventory_entry = f"\t{inventory_entry}"
                    vehicle_inventory_entry = (
                        self.convert_breed_inventory_entry_to_game_item_info(
                            inventory_entry
                        )
                    )
                    if vehicle_inventory_entry:
                        vehicle_inventories[vehicle_name].append(
                            vehicle_inventory_entry
                        )
        self.vehicle_inventories = vehicle_inventories

    def get_vehicle_properties(self) -> None:
        """Load and process vehicle properties from game files."""
        assert self.game_vehicles_path.exists(), "Game vehicles path does not exist!"
        vehicle_files_paths = self.get_vehicle_files_paths()
        vehicle_properties = {}
        vehicle_fuel_properties = {}
        for file_path in vehicle_files_paths:

            file_path_split = file_path.split("\\")
            vehicle_name = re.sub(r"\.(def)$", "", file_path_split[-1])

            with open(file_path, "r") as file:
                content = file.read()
                pattern = r'\(include\s+"\/properties\/([^"/.]+)\.ext"\)'
                matches = re.findall(pattern, content)
                vehicle_properties[vehicle_name] = matches

            with open(file_path, "r") as file:
                content = file.read()
                pattern = r"fuel\((\d+)\)"
                match = re.search(pattern, content)
                vehicle_fuel_properties[vehicle_name] = (
                    int(match.group(1)) if match else -1
                )

        for file_path in vehicle_files_paths:
            file_path_split = file_path.split("\\")
            vehicle_name = re.sub(r"\.(def)$", "", file_path_split[-1])

            if vehicle_properties[vehicle_name] == []:
                with open(file_path, "r") as file:
                    content = file.read()
                    pattern = r'\(include\s+"([^"/.]+)\.inc"\)'
                    matches = re.findall(pattern, content)
                    property_name = f"{matches[0]}.inc"
                    vehicle_properties[vehicle_name] = vehicle_properties[property_name]
                    vehicle_fuel_properties[vehicle_name] = vehicle_fuel_properties[
                        property_name
                    ]

        for vehicle_name, properties in vehicle_properties.items():
            assert properties != []

        self.vehicles_properties_lists = vehicle_properties
        self.vehicles_fuel_properties = vehicle_fuel_properties

    def get_properties_files_paths(self) -> list[str]:
        """Get paths to all properties files.

        Returns:
            list[str]: List of properties file paths
        """
        properties_files_paths = glob.glob(
            f"{str(self.game_properties_path)}/**/*", recursive=True
        )
        properties_files_paths = [
            file_path
            for file_path in properties_files_paths
            if not os.path.isdir(file_path)
        ]

        properties_files_paths = list(set(properties_files_paths))

        return properties_files_paths

    def get_inventory_size_and_entries_from_properties(
        self, properties_files_paths: list[str]
    ) -> tuple[dict, dict]:
        """Extract inventory sizes and entries from properties files.

        Args:
            properties_files_paths: List of properties file paths

        Returns:
            tuple[dict, dict]: Properties inventory entries and sizes
        """
        properties_inventory_entries = {}
        properties_inventory_sizes = {}
        for file_path in properties_files_paths:
            file_path_split = file_path.split("\\")
            property_name = file_path_split[-1]
            property_name = re.sub(r"\.ext$", "", property_name)
            with open(file_path, "r") as file:
                current_property_inventory_entries = []
                for line in file:
                    if '{extender "inventory"' in line:
                        for subline in file:
                            if "{Size" in subline or "{size" in subline:
                                pattern = r"\{Size\s+(\d+)\s+(\d+)\}"
                                match = re.search(pattern, subline)
                                if match:
                                    properties_inventory_sizes[property_name] = {
                                        "x": int(match.group(1)),
                                        "y": int(match.group(2)),
                                    }
                            elif "{item" in subline and ";{item" not in subline:
                                current_property_inventory_entries.append(subline)
                            if subline == "\t}\n":
                                break
                        break

                if property_name in properties_inventory_entries:
                    properties_inventory_entries[property_name].extend(
                        current_property_inventory_entries
                    )
                else:
                    properties_inventory_entries[property_name] = (
                        current_property_inventory_entries
                    )
        return properties_inventory_sizes, properties_inventory_entries

    def resolve_properties_inclusions(self, properties_files_paths: list[str]) -> dict:
        def resolve_inclusions_for_property(property_file_path: str) -> list[str]:
            pattern = r'\(include\s+"([^"]+)\.ext"\)'
            with open(property_file_path, "r") as file:
                content = file.read()
                matches = re.finditer(pattern, content)
                current_inclusions = []
                for match in matches:
                    property_name = match.group(1)
                    if "/properties/" in property_name:
                        property_name = re.sub(r"/properties/", "", property_name)

                    included_property_file_path = str(
                        self.game_properties_path / f"{property_name}.ext"
                    )
                    current_inclusions.append(included_property_file_path)
                    resolved_inclusions = resolve_inclusions_for_property(
                        included_property_file_path
                    )
                    current_inclusions.extend(resolved_inclusions)
                return current_inclusions

        inclusions = {}
        for file_path in properties_files_paths:
            resolved_inclusions = resolve_inclusions_for_property(file_path)
            resolved_inclusions.append(file_path)
            file_path_split = file_path.split("\\")
            property_name = file_path_split[-1]
            property_name = re.sub(r"\.ext$", "", property_name)
            inclusions[property_name] = resolved_inclusions
        return inclusions

    def get_inventory_information_from_properties(self) -> None:
        """Load inventory information from properties files."""
        assert (
            self.game_properties_path.exists()
        ), "Game properties path does not exist!"
        properties_files_paths = self.get_properties_files_paths()
        properties_files_paths = [
            file_path for file_path in properties_files_paths if ".ext" in file_path
        ]
        inclusions = self.resolve_properties_inclusions(properties_files_paths)

        properties_inventory_sizes_all = {}
        properties_inventory_entries_all = {}
        for property_name, included_files in inclusions.items():

            properties_inventory_sizes, properties_inventory_entries = (
                self.get_inventory_size_and_entries_from_properties(included_files)
            )

            if properties_inventory_sizes == {}:
                properties_inventory_sizes[property_name] = {"x": 0, "y": 0}

            merged_properties_inventory_entries = {property_name: []}
            for _, inventory_entries in properties_inventory_entries.items():
                merged_properties_inventory_entries[property_name].extend(
                    inventory_entries
                )

            for key, value in properties_inventory_sizes.items():
                properties_inventory_sizes_all[property_name] = value

            for key, value in merged_properties_inventory_entries.items():
                properties_inventory_entries_all[key] = value

        self.properties_inventory_sizes = properties_inventory_sizes_all
        self.properties_inventory_entries = properties_inventory_entries_all

    def get_squads_compositions(self) -> None:
        """Load squad compositions from conquest units files."""
        assert (
            self.game_conquest_units_path.exists()
        ), "Game conquest units path does not exist!"
        assert self.infantry_costs != {}, "Infantry costs are not set!"

        files_with_squads_compositions = glob.glob(
            f"{str(self.game_conquest_units_path)}/**/*", recursive=True
        )
        files_with_squads_compositions = [
            file_path
            for file_path in files_with_squads_compositions
            if not os.path.isdir(file_path) and ".set" in file_path
        ]
        files_with_squads_compositions = [
            file_path
            for file_path in files_with_squads_compositions
            if "units_" in file_path
        ]

        squad_compositions_string_entries = []
        for file_path in files_with_squads_compositions:
            with open(file_path, "r") as file:
                for line in file:
                    if line[0] == ";":
                        continue
                    current_entry = ""
                    if "{" in line and "\t{" not in line:
                        current_entry += line
                        for subline in file:
                            if subline == "}" or subline == "}\n":
                                current_entry += subline
                                break
                            else:
                                current_entry += subline
                    elif '("' in line:
                        current_entry += line
                    else:
                        continue
                    squad_compositions_string_entries.append(current_entry)

        # self.process_squads_compositions_entires(squad_compositions_string_entries)
        squad_compositions = self.process_squads_compositions_entires(
            squad_compositions_string_entries
        )

        squad_compositions = self.calculate_squad_composition_costs(squad_compositions)

        self.squad_compositions = squad_compositions

    def process_squads_compositions_entires(
        self, squad_compositions_string_entries: list[str]
    ) -> None:
        """Process squad composition entries from string data.

        Args:
            squad_compositions_string_entries: List of squad composition strings
        """
        squad_compositions = {}
        for entry in squad_compositions_string_entries:
            if any(
                pattern in entry
                for pattern in [
                    "not_for_sale",
                    "_barrage",
                    "airstrike",
                ]
            ):
                continue

            entry = entry.strip("{}()")
            entry = re.sub("\n", " ", entry)
            entry = re.sub("\t", " ", entry)
            entry = re.sub("  ", " ", entry)

            entry_parts = entry.split(" ")
            joined_entry = " ".join(entry_parts)
            name = ""
            side = ""
            period = ""
            cost = 0
            members = {}

            is_vehicle = False
            if '("vehicle' in joined_entry or '("squad_vehicle' in joined_entry:
                name = entry_parts[0].strip('"')
                is_vehicle = True
            for i, entry_part in enumerate(entry_parts):
                if "squad_with" in entry_part:
                    continue
                elif "side" in entry_part:
                    side = re.sub("side", "", entry_part)
                    side = side.strip("()")
                elif "period" in entry_part:
                    period = re.sub("period", "", entry_part)
                    period = period.strip("()")
                elif "name" in entry_part:
                    name = re.sub("name", "", entry_part)
                    name = name.strip("()")
                elif "vehicle(" in entry_part:
                    vehicle_name = re.sub("vehicle", "", entry_part)
                    vehicle_name = vehicle_name.strip("()")
                    members[vehicle_name] = 1
                elif "{cost" in entry_part:
                    cost_str = entry_parts[i + 1]
                    cost_str_parts = cost_str.split("}")
                    cost_str = cost_str_parts[0]
                    cost_str = cost_str.strip("{}")
                    cost += int(cost_str)
                else:
                    if any(
                        key_word in entry_part
                        for key_word in [
                            "min_stage",
                            "max_stage",
                            "cw",
                            "cp",
                            "condition",
                            "action",
                            "scf",
                        ]
                    ):
                        continue
                    pattern = r"(\w+)\(([^)]+)\)"
                    matches = re.findall(pattern, entry_part)
                    for match in matches:
                        content = match[1]
                        content_parts = content.split(":")
                        member_name = content_parts[0]
                        member_extended_name = f"mp/{side}/{period}/{member_name}"
                        member_count = content_parts[1]
                        members[member_extended_name] = int(member_count)

            if is_vehicle and '("squad_vehicle' not in joined_entry:
                members[name] = 1

            squad_composition_info = SquadCompositionInfo(
                name=name + f"({side})" if not is_vehicle else name,
                side=side,
                period=period,
                cost=cost,
                members=members,
            )

            squad_compositions[squad_composition_info.name] = squad_composition_info
        return squad_compositions

    def calculate_squad_composition_costs(
        self, squad_compositions: dict[str, SquadCompositionInfo]
    ) -> dict[str, SquadCompositionInfo]:
        """Calculate total costs for squad compositions.

        Args:
            squad_compositions: Dictionary of squad compositions

        Returns:
            dict[str, SquadCompositionInfo]: Updated squad compositions with costs
        """
        for squad_name, squad_info in squad_compositions.items():
            total_cost = squad_info.cost
            has_vehicle = False
            for member_name, member_count in squad_info.members.items():
                if member_name in self.infantry_costs:
                    member_cost = self.infantry_costs[member_name]
                    total_cost += member_cost * member_count
                elif member_name in squad_compositions:
                    vehicle_squad_info = squad_compositions[member_name]
                    has_vehicle = True
                    if squad_info != vehicle_squad_info:
                        vehicle_cost = vehicle_squad_info.cost
                        total_cost += vehicle_cost * member_count
                        self.vehicles_costs[member_name] = vehicle_cost
                else:
                    self.logger.log(
                        f"Cost for {member_name} not found in infantry costs or squad compositions."
                    )
            if has_vehicle:
                total_cost = math.ceil(total_cost / 5) * 5
            squad_info.cost = int(total_cost)
        return squad_compositions

    def get_infantry_costs(self) -> None:
        """Load infantry costs from conquest units files."""
        assert (
            self.game_conquest_units_path.exists()
        ), "Game conquest units path does not exist!"

        files_with_infantry_costs = glob.glob(
            f"{str(self.game_conquest_units_path)}/**/*", recursive=True
        )
        files_with_infantry_costs = [
            file_path
            for file_path in files_with_infantry_costs
            if not os.path.isdir(file_path) and ".set" in file_path
        ]
        files_with_infantry_costs = [
            file_path for file_path in files_with_infantry_costs if "inf_" in file_path
        ]

        infantry_costs = {}
        for file_path in files_with_infantry_costs:
            with open(file_path, "r") as file:
                for line in file:
                    if '{"mp' in line:
                        line = re.sub("\n", "", line)
                        line = re.sub("\t", " ", line)
                        line = re.sub("  ", " ", line)
                        line = line.strip("{}")
                        line_parts = line.split(" ")
                        name = ""
                        cost = 0
                        for part in line_parts:
                            if "mp/" in part:
                                part_split = part.split("(")
                                name = part_split[0]
                                name = name.strip('"')
                            elif "cost" in part:
                                cost_str = re.sub("cost", "", part)
                                cost_str = cost_str.strip("(){};")
                                cost = float(cost_str)
                        infantry_costs[name] = cost

        infantry_costs = self.handle_infantry_cost_exceptions(infantry_costs)

        self.infantry_costs = infantry_costs

    def handle_infantry_cost_exceptions(
        self, infantry_costs: dict[str, int]
    ) -> dict[str, int]:
        exceptions_names_costs = {
            "mp/rus/late/sapper_nco": 10,
            "mp/usa/mid/platoon_com": 15,
            "mp/usa/late/late_driver_m3": 10,
            "60mm_m2_late": 170,
            "mp/usa/late/101st_eng_at_m1a1": 73,
        }
        infantry_costs.update(exceptions_names_costs)

        return infantry_costs

    def create_vehicles_properties(self) -> None:
        """Create vehicles properties from loaded data."""
        assert (
            self.vehicles_properties_lists != {}
        ), "Vehicles properties lists are empty!"
        vehicles_properties = {}
        for (
            vehicle_name,
            vehicle_property_types,
        ) in self.vehicles_properties_lists.items():
            vehicles_properties[vehicle_name] = vehicle_property_types[0]

        assert vehicles_properties != {}
        self.vehicles_properties = vehicles_properties

    def find_weapons_in_breed_inventory_entries(
        self, breed_inventory_entries: list[BreedItemInfo]
    ) -> list[str]:
        """Find weapons in breed inventory entries.

        Args:
            breed_inventory_entries: List of breed item information

        Returns:
            list[str]: List of weapon names found
        """
        found_weapons = []
        for item in breed_inventory_entries:
            if item.game_item_name in self.weapons_list:
                found_weapons.append(item.game_item_name)
        return found_weapons

    def get_campaign_status_information(self) -> None:
        """Load campaign status information from file."""
        assert (
            self.campaign_status_file_path.exists()
        ), "Campaign status file path does not exist!"

        with open(self.campaign_status_file_path, "r") as file:
            campaign_status_values = {}
            for line in file:
                if not any(
                    pattern in line
                    for pattern in [
                        "{mp",
                        "{sp",
                        "{ap",
                        "{rp",
                        "{army",
                    ]
                ):
                    continue

                line = re.sub(r"[\t\n]", "", line)
                line = line.strip("{}")
                line_split = line.split(" ")
                status_key = line_split[0]
                status_value = line_split[1]
                if status_key == "army":
                    campaign_status_values[status_key] = status_value
                else:
                    campaign_status_values[status_key] = float(status_value)
        self.campaign_status_info = CampaignStatusInfo(**campaign_status_values)

    def get_item_weights(self) -> None:
        """Load item weights from game files."""
        assert self.game_items_path.exists(), "Game items path does not exist!"
        item_files_paths = self.get_item_files_paths()
        item_weights = {}
        for item_file_path in item_files_paths:
            item_name = item_file_path.split("\\")[-1]

            with open(item_file_path, "r") as item_file:
                item_info = item_file.read()

                if any(pattern in item_info for pattern in EXCLUDED_PATTERNS):
                    continue

                if f"{{{MASS_KEYWORD}" in item_info:
                    if mass_match := re.search(
                        rf"\{{{MASS_KEYWORD}\s+(\d+\.?\d*)\}}", item_info
                    ):
                        item_weights[item_name] = float(mass_match.group(1))
                    else:
                        self.logger.log(f"No mass in: {item_info}")
                    continue

                if from_match := re.search(r"\{from\s+\"(.*?)\"", item_info):
                    pattern = from_match.group(1)
                    pattern_to_seek = self.create_correct_pattern_to_seek(pattern)
                    item_weights[item_name] = {"pattern_to_seek": pattern_to_seek}
                else:
                    continue

        updated_item_weights = {}
        for k, v in item_weights.items():
            if not isinstance(v, dict):
                updated_item_weights[k] = v
                continue

            pattern = v["pattern_to_seek"]
            current_weight = item_weights.get(pattern) or item_weights.get(
                f"{pattern}.weapon"
            )
            if current_weight is None or isinstance(current_weight, dict):
                updated_item_weights[k] = 0.0
            else:
                updated_item_weights[k] = float(current_weight)

        self.item_weights = updated_item_weights
