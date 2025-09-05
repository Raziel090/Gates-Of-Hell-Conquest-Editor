"""Entity inventory management and item manipulation for game units."""

from dataclasses import dataclass
import re

import numpy as np

from src.exceptions import ItemFitError
from src.knowledge_base import KnowledgeBase, WeaponInfo
from src.constants import (
    # Default values and constants
    DEFAULT_AMOUNT,
    DEFAULT_PROPERTY_NAME,
    EMPTY_CELL_VALUE,
    OCCUPIED_CELL_VALUE,
    INVALID_AMOUNT,
    # String patterns and separators
    DOT_SEPARATOR,
    SPACE_SEPARATOR,
    EMPTY_STRING,
    NEWLINE,
    QUOTE_CHAR,
    # Regex patterns
    QUOTE_ITEM_PATTERN,
    QUOTED_STRING_PATTERN,
    AMOUNT_PATTERN,
    CELL_PATTERN,
    CELL_VALUES_PATTERN,
    FILL_AMOUNT_PATTERN,
    # Keywords and markers
    FILLING_KEYWORD,
    FILLED_KEYWORD,
    HUMAN_KEYWORD,
    # Item size properties
    X_SIZE_KEY,
    Y_SIZE_KEY,
    # Error messages
    INVENTORY_MATRIX_ERROR,
    ITEM_FIT_ERROR_TEMPLATE,
    ADD_ITEM_ERROR_TEMPLATE,
    # String format templates
    ENTITY_INVENTORY_STR_TEMPLATE,
    ITEM_ENTRY_PREFIX,
    ITEM_NAME_QUOTE_TEMPLATE,
    AMOUNT_FORMAT,
    CELL_FORMAT,
    AMOUNT_REPLACEMENT_TEMPLATE,
    # Inventory file format
    INVENTORY_HEADER_TEMPLATE,
    BOX_OPEN,
    BOX_CLEAR,
    BOX_CLOSE,
    INVENTORY_CLOSE,
)


@dataclass
class GameItemInfo:
    """Store game item information including position and amount."""

    game_item_name: str
    amount: int
    cell_x: int
    cell_y: int


class EntityInventory:
    """Manage inventory operations for game entities and units."""

    def __init__(
        self,
        squad_id: int,
        entity_id: str,
        entity_breed: str,
        inventory_entries: list[str],
        supplies: int,
        resources: int,
        fuel: float,
        knowledge_base: KnowledgeBase,
    ):
        """Initialize entity inventory with game data and knowledge base.

        Args:
            squad_id (int): ID of the squad containing this entity
            entity_id (str): Unique hex ID of the entity
            entity_breed (str): Breed type of the entity
            inventory_entries (list[str]): Raw inventory data entries
            supplies (int): Current supplies amount
            resources (int): Current resources amount
            fuel (float): Current fuel amount
            knowledge_base (KnowledgeBase): Game knowledge database
        """
        self.squad_id = squad_id
        self.entity_id = entity_id
        self.entity_breed = entity_breed
        self.inventory_entries = inventory_entries
        self.supplies = supplies
        self.resources = resources
        self.fuel = fuel
        self.knowledge_base = knowledge_base
        self.logger = knowledge_base.logger

        self.inventory_matrix = None
        self.item_counts = None

    def __str__(self) -> str:
        """Return string representation of entity inventory.

        Returns:
            str: Formatted inventory information
        """
        entries_str = EMPTY_STRING.join(entry for entry in self.inventory_entries)
        return ENTITY_INVENTORY_STR_TEMPLATE.format(
            self.squad_id, self.entity_id, entries_str, self.supplies, self.fuel
        )

    def convert_inventory_entry_to_game_item_info(
        self, inventory_item_entry: str
    ) -> GameItemInfo:
        """Parse inventory entry string into structured item information.

        Args:
            inventory_item_entry (str): Raw inventory entry string

        Returns:
            GameItemInfo: Parsed item information with name, amount, and position
        """
        quote_item_pattern = QUOTE_ITEM_PATTERN
        quoted_string_pattern = QUOTED_STRING_PATTERN

        matches = re.finditer(quote_item_pattern, inventory_item_entry)

        for match in matches:
            quoted_items = re.findall(quoted_string_pattern, match.group(0))

        game_item_name = DOT_SEPARATOR.join(quoted_items)

        amount_pattern = AMOUNT_PATTERN
        amount = DEFAULT_AMOUNT
        amount_match = re.search(amount_pattern, inventory_item_entry)
        if amount_match and FILLING_KEYWORD not in inventory_item_entry:
            amount = int(amount_match.group(1))

        cell_pattern = CELL_PATTERN
        cell_values_pattern = CELL_VALUES_PATTERN

        cell_match = re.findall(cell_pattern, inventory_item_entry)[0]
        cell_match = re.findall(cell_values_pattern, cell_match)
        cell_x = cell_match[0]
        cell_y = cell_match[1]

        return GameItemInfo(
            game_item_name=game_item_name, amount=amount, cell_x=cell_x, cell_y=cell_y
        )

    def create_inventory_matrix(self) -> None:
        """Create numpy matrix representing inventory grid occupancy."""
        property_name = self.knowledge_base.vehicles_properties.get(
            self.entity_breed, DEFAULT_PROPERTY_NAME
        )
        inventory_matrix_size = self.knowledge_base.properties_inventory_sizes[
            property_name
        ]
        inventory_matrix_size = (
            inventory_matrix_size[X_SIZE_KEY],
            inventory_matrix_size[Y_SIZE_KEY],
        )

        inventory_matrix = np.zeros(inventory_matrix_size, dtype=int)
        inventory_entries = self.inventory_entries

        for inventory_entry in inventory_entries:
            game_item_info = self.convert_inventory_entry_to_game_item_info(
                inventory_entry
            )
            item_name = game_item_info.game_item_name
            start_cell_x = int(game_item_info.cell_x)
            start_cell_y = int(game_item_info.cell_y)

            item_size = self.knowledge_base.item_sizes[item_name]
            x_size = int(item_size[X_SIZE_KEY])
            y_size = int(item_size[Y_SIZE_KEY])
            for i in range(x_size):
                for j in range(y_size):
                    assert (
                        inventory_matrix[start_cell_x + i][start_cell_y + j]
                        != OCCUPIED_CELL_VALUE
                    )
                    inventory_matrix[start_cell_x + i][
                        start_cell_y + j
                    ] = OCCUPIED_CELL_VALUE

        self.inventory_matrix = inventory_matrix

    def find_inventory_space_for_item(self, item_name: str) -> dict[str, str]:
        """Find available space in inventory for specified item.

        Args:
            item_name (str): Name of item to find space for

        Returns:
            dict[str, str]: Game item info with available position

        Raises:
            ItemFitError: If item cannot fit in available inventory space
        """
        assert self.inventory_matrix is not None, INVENTORY_MATRIX_ERROR
        item_size = self.knowledge_base.item_sizes[item_name]
        x_size = int(item_size[X_SIZE_KEY])
        y_size = int(item_size[Y_SIZE_KEY])

        for start_cell_y in range(self.inventory_matrix.shape[1]):
            for start_cell_x in range(self.inventory_matrix.shape[0]):
                item_fit_checks = np.zeros((x_size, y_size), dtype=int)
                if (
                    self.inventory_matrix[start_cell_x][start_cell_y]
                    == EMPTY_CELL_VALUE
                ):
                    for i in range(x_size):
                        for j in range(y_size):
                            if start_cell_x + i >= self.inventory_matrix.shape[0]:
                                break
                            if start_cell_y + j >= self.inventory_matrix.shape[1]:
                                break
                            if (
                                self.inventory_matrix[start_cell_x + i][
                                    start_cell_y + j
                                ]
                                == EMPTY_CELL_VALUE
                            ):
                                item_fit_checks[i][j] = OCCUPIED_CELL_VALUE
                            else:
                                break
                    if np.all(item_fit_checks):
                        return GameItemInfo(
                            game_item_name=item_name,
                            amount=INVALID_AMOUNT,
                            cell_x=start_cell_x,
                            cell_y=start_cell_y,
                        )

        raise ItemFitError(
            ITEM_FIT_ERROR_TEMPLATE.format(item_name, item_size, self.entity_id)
        )

    def prepare_inventory_item_entry(
        self,
        game_item_info: GameItemInfo,
        amount: int = 1,
    ) -> str:
        """Format game item info into inventory entry string.

        Args:
            game_item_info (GameItemInfo): Item information to format
            amount (int): Quantity of item (default: 1)

        Returns:
            str: Formatted inventory entry string
        """
        entry_str = ITEM_ENTRY_PREFIX
        item_name_split = game_item_info.game_item_name.split(DOT_SEPARATOR)
        for item_name_part in item_name_split:
            entry_str += ITEM_NAME_QUOTE_TEMPLATE.format(item_name_part)
        if amount > DEFAULT_AMOUNT:
            entry_str += AMOUNT_FORMAT.format(amount)
        entry_str += CELL_FORMAT.format(game_item_info.cell_x, game_item_info.cell_y)
        return entry_str

    def add_item_to_inventory(self, item_name: str, amount: int = 1) -> bool:
        """Add item to inventory if space is available.

        Args:
            item_name (str): Name of item to add
            amount (int): Quantity to add (default: 1)

        Returns:
            bool: True if item was added successfully, False otherwise
        """
        try:
            game_item_info = self.find_inventory_space_for_item(item_name)
            inventory_entry = self.prepare_inventory_item_entry(
                game_item_info=game_item_info,
                amount=amount,
            )
            self.inventory_entries.append(inventory_entry)
            self.create_inventory_matrix()
            return True
        except ItemFitError as err:
            self.logger.log(ADD_ITEM_ERROR_TEMPLATE.format(err))
            return False

    def fill_item_in_inventory(self, item_name: str, max_amount: int = 1) -> int:
        """Fill existing item in inventory up to maximum amount.

        Args:
            item_name (str): Name of item to fill
            max_amount (int): Maximum amount to fill to (default: 1)

        Returns:
            int: Amount actually added to existing item
        """
        item_name_split = item_name.split(DOT_SEPARATOR)
        item_name_split = [
            ITEM_NAME_QUOTE_TEMPLATE.format(part).strip() for part in item_name_split
        ]
        item_name = SPACE_SEPARATOR.join(item_name_split)

        pattern = FILL_AMOUNT_PATTERN
        for i, inventory_entry in enumerate(self.inventory_entries):
            if FILLING_KEYWORD in inventory_entry or FILLED_KEYWORD in inventory_entry:
                continue
            if item_name in inventory_entry:
                match = re.findall(pattern, inventory_entry)
                if match:
                    current_amount = match[0][0]
                    current_amount = int(current_amount)
                    if current_amount < max_amount:
                        inventory_entry = re.sub(
                            AMOUNT_REPLACEMENT_TEMPLATE.format(current_amount),
                            AMOUNT_REPLACEMENT_TEMPLATE.format(str(max_amount)),
                            inventory_entry,
                        )
                        self.inventory_entries[i] = inventory_entry
                        self.create_inventory_matrix()
                        return max_amount - current_amount
        return 0

    def count_items_in_inventory(self) -> None:
        """Count total amounts of each item type in inventory."""
        item_counts = {}
        for inventory_entry in self.inventory_entries:
            game_item_info = self.convert_inventory_entry_to_game_item_info(
                inventory_entry
            )
            item_name = game_item_info.game_item_name
            if item_name in item_counts:
                item_counts[item_name] += game_item_info.amount
            else:
                item_counts[item_name] = game_item_info.amount
        self.item_counts = item_counts

    def find_gun_entries_in_inventory(self) -> list[WeaponInfo]:
        """Find all weapon entries present in inventory.

        Returns:
            list[WeaponInfo]: List of weapon information for found weapons
        """
        guns = []
        for inventory_entry in self.inventory_entries:
            game_item_info = self.convert_inventory_entry_to_game_item_info(
                inventory_entry
            )
            item_name = game_item_info.game_item_name
            for weapon_info in self.knowledge_base.weapons_info_list:
                if item_name == weapon_info.weapon_name:
                    guns.append(weapon_info)
        return guns

    def prepare_inventory_for_saving(self) -> str:
        """Format complete inventory data for saving to campaign file.

        Returns:
            str: Formatted inventory string ready for campaign file
        """
        inventory_str = INVENTORY_HEADER_TEMPLATE.format(self.entity_id)
        inventory_str += BOX_OPEN
        inventory_str += BOX_CLEAR
        for inventory_entry in self.inventory_entries:
            inventory_str += inventory_entry
        inventory_str += BOX_CLOSE
        inventory_str += INVENTORY_CLOSE
        return inventory_str
