"""Game manager for squad and inventory operations."""

import os
from pathlib import Path
from src.console_logger import ConsoleLogger
from src.data_classes import SquadInfo, SquadInventory
from src.data_manager import DataManager
from src.knowledge_base import KnowledgeBase
from src.constants import (
    # File and directory constants
    DECEASED_MEMBER_ID,
)

# File and directory constants (local to game manager)
RESOURCE_DIR = "resource"
GAMELOGIC_FILE = "gamelogic.pak"
ENTITY_DIR = "entity"
VEHICLE_FILE = "-vehicle.pak"
PROPERTIES_FILE = "properties.pak"

# Error messages
NO_SQUADS_ERROR = "There are no squads information!"


class GameManager:
    """Manage game data operations and squad inventories."""

    def __init__(
        self,
        game_install_dir_path: str,
        campaign_file_path: str,
        data_dir_path: str,
        logger: ConsoleLogger,
    ) -> None:
        """Initialize GameManager with required paths.

        Args:
            game_install_dir_path (str): Path to game installation directory
            campaign_file_path (str): Path to campaign save file
            data_dir_path (str): Path to working data directory
            logger (ConsoleLogger): Logger instance for messages
        """
        gamelogic_file_path = (
            Path(game_install_dir_path) / RESOURCE_DIR / GAMELOGIC_FILE
        )
        campaign_save_file_path = Path(campaign_file_path)
        data_dir_path = Path(data_dir_path)

        vehicle_file_path = (
            Path(game_install_dir_path) / RESOURCE_DIR / ENTITY_DIR / VEHICLE_FILE
        )

        properties_file_path = (
            Path(game_install_dir_path) / RESOURCE_DIR / PROPERTIES_FILE
        )

        os.makedirs(data_dir_path, exist_ok=True)

        self.logger = logger

        self.knowledge_base = KnowledgeBase(
            data_dir_path=data_dir_path,
            gamelogic_file_path=gamelogic_file_path,
            logger=self.logger,
        )

        self.data_manager = DataManager(
            data_dir_path=data_dir_path,
            gamelogic_file_path=gamelogic_file_path,
            vehicle_file_path=vehicle_file_path,
            properties_file_path=properties_file_path,
            campaign_save_file_path=campaign_save_file_path,
            knowledge_base=self.knowledge_base,
            logger=self.logger,
        )

        self.knowledge_base.init_knowledge_base()

        self.squads: list[SquadInfo] = []
        self.squads_entries: list[str] = []
        self.squads_inventories: list[SquadInventory] = []

    def prepare_squads_and_inventories(
        self, keep_deceased_members: bool = False
    ) -> None:
        """Extract squad information and inventories from campaign data.

        Args:
            keep_deceased_members (bool): Whether to include deceased members
        """
        self.squads, self.squads_entries = self.data_manager.extract_squads_information(
            keep_deceased_members=keep_deceased_members
        )
        self.squads_inventories = self.get_all_inventories()

    def get_all_inventories(self) -> list[SquadInventory]:
        """Retrieve inventory data for all squads.

        Returns:
            list[SquadInventory]: List of squad inventory objects
        """
        assert self.squads, NO_SQUADS_ERROR

        squads_inventories = []
        for squad_info in self.squads:
            current_squad_inventories = self.get_all_inventories_for_squad(
                squad_info.squad_id, squad_info.squad_members
            )
            squads_inventories.append(current_squad_inventories)

        return squads_inventories

    def get_all_inventories_for_squad(
        self, squad_id: int, squad_members: list[str]
    ) -> SquadInventory:
        """Extract inventory data for all members of a specific squad.

        Args:
            squad_id (int): Unique identifier of the squad
            squad_members (list[str]): List of squad member IDs as hex strings

        Returns:
            SquadInventory: Squad inventory data for all valid members
        """
        squad_inventories = SquadInventory(squad_id=squad_id, inventories={})
        for squad_member_id in squad_members:
            if squad_member_id == DECEASED_MEMBER_ID:
                continue
            squad_member_breed = self.data_manager.extract_squad_member_breed(
                squad_member_id=squad_member_id
            )
            squad_member_inventory = self.data_manager.extract_squad_member_inventory(
                squad_id=squad_id,
                squad_member_id=squad_member_id,
                squad_member_breed=squad_member_breed,
            )

            squad_inventories.inventories[squad_member_id] = squad_member_inventory

        return squad_inventories
