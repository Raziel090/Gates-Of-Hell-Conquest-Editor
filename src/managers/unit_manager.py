"""Unit management for moving and exchanging squad members."""

import fileinput
import re
from src.console_logger import ConsoleLogger

from src.managers.game_manager import GameManager


# Constants for campaign file processing
CAMPAIGN_SQUADS_MARKER = "{CampaignSquads"
SPACE_SEPARATOR = " "
EMPTY_STRING = ""
CLOSING_BRACE_REGEX = r"}$"
UNIT_REMOVAL_FORMAT = " {}"
UNIT_ADDITION_FORMAT = " {}}}"
LINE_SPLIT_START_INDEX = 2
REGEX_SINGLE_COUNT = 1


class UnitManager(GameManager):
    """Manage unit movement and exchange between squads."""

    def __init__(
        self,
        game_install_dir_path: str,
        campaign_file_path: str,
        data_dir_path: str,
        logger: ConsoleLogger,
    ) -> None:
        """Initialize UnitManager with game paths and logger.

        Args:
            game_install_dir_path (str): Path to game installation directory
            campaign_file_path (str): Path to campaign save file
            data_dir_path (str): Path to working data directory
            logger (ConsoleLogger): Logger instance for messages
        """
        super().__init__(
            game_install_dir_path=game_install_dir_path,
            campaign_file_path=campaign_file_path,
            data_dir_path=data_dir_path,
            logger=logger,
        )

    def move_unit(
        self,
        unit_squad_id: int,
        unit_id: int,
        target_squad_id: int,
        target_unit_id: "int | None" = None,
        target_unit_position: int | None = None,
    ) -> None:
        """Move or exchange unit between squads.

        Args:
            unit_squad_id (int): Source squad identifier
            unit_id (int): Unit identifier to move
            target_squad_id (int): Target squad identifier
            target_unit_id (int | None): Target unit for exchange (optional)
            target_unit_position (int | None): Position in target squad (optional)
        """
        with fileinput.input(
            self.data_manager.campaign_data_file_path, inplace=True
        ) as file:
            scan = 0
            reached_squads = False
            for line in file:
                line = line.rstrip()
                if reached_squads:
                    if target_unit_id is None:
                        line = self._move_unit_to_squad(
                            line, scan, unit_squad_id, unit_id, target_squad_id
                        )
                    else:
                        line = self._exchange_units(
                            line,
                            scan,
                            unit_squad_id,
                            unit_id,
                            target_squad_id,
                            target_unit_id,
                            target_unit_position,
                        )
                    scan += 1
                if CAMPAIGN_SQUADS_MARKER in line:
                    reached_squads = True
                print(line)

    def _move_unit_to_squad(
        self,
        line: str,
        scan: int,
        unit_squad_id: int,
        unit_id: int,
        target_squad_id: int,
    ) -> None:
        """Move unit from one squad to another.

        Args:
            line (str): Current line being processed
            scan (int): Current squad index
            unit_squad_id (int): Source squad identifier
            unit_id (int): Unit identifier to move
            target_squad_id (int): Target squad identifier

        Returns:
            str: Modified line
        """
        if scan == unit_squad_id:
            line = re.sub(UNIT_REMOVAL_FORMAT.format(unit_id), EMPTY_STRING, line)
        if scan == target_squad_id:
            line = re.sub(
                CLOSING_BRACE_REGEX, UNIT_ADDITION_FORMAT.format(unit_id), line
            )
        return line

    def _exchange_units(
        self,
        line: str,
        scan: int,
        unit_squad_id: int,
        unit_id: str,
        target_squad_id: int,
        target_unit_id: str,
        target_unit_position: int,
    ) -> None:
        """Exchange positions of two units between squads.

        Args:
            line (str): Current line being processed
            scan (int): Current squad index
            unit_squad_id (int): Source squad identifier
            unit_id (str): Source unit identifier
            target_squad_id (int): Target squad identifier
            target_unit_id (str): Target unit identifier
            target_unit_position (int): Position in target squad

        Returns:
            str: Modified line
        """
        if scan == unit_squad_id:
            line = re.sub(unit_id, target_unit_id, line, count=REGEX_SINGLE_COUNT)
        elif scan == target_squad_id:
            line_split = line.split(SPACE_SEPARATOR)
            ids = line_split[LINE_SPLIT_START_INDEX:]
            ids[target_unit_position] = re.sub(
                target_unit_id, unit_id, ids[target_unit_position]
            )
            line = SPACE_SEPARATOR.join(line_split[:LINE_SPLIT_START_INDEX] + ids)

        return line

    def save_changes(self) -> None:
        """Save campaign changes to files."""
        self.data_manager.save_campaign_status_info()

        self.data_manager.save_campaign_file()
