"""Vehicle appearance manager for campaign Entity customization."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Callable

from src.console_logger import ConsoleLogger
from src.managers.game_manager import GameManager


ENTITY_START_PATTERN = re.compile(r'^\s*\{Entity\s+"([^"]+)"\s+(\S+)')
NUMBER_PATTERN = re.compile(r'(\{number\s+)(\d+)(\s*\})')
DIGIT_FOLDER_PATTERN = re.compile(r'(\{digit_folder\s+")([^"]*)("\s*\})')


@dataclass(frozen=True)
class VehicleAppearanceEntity:
    """Vehicle entity information available for appearance edits."""

    breed: str
    entity_id: str
    has_armor_section: bool
    has_enumerator: bool
    number_value: str | None
    digit_folder_value: str | None

    @property
    def display_name(self) -> str:
        """Display name used by GUI selectors."""
        return f"{self.breed} ({self.entity_id})"


@dataclass(frozen=True)
class EntityBlock:
    """Parsed Entity block slice from campaign file text."""

    breed: str
    entity_id: str
    start_offset: int
    end_offset: int
    text: str


class VehicleAppearanceManager(GameManager):
    """Manage appearance customization for Entity entries in campaign saves."""

    def __init__(
        self,
        game_install_dir_path: str,
        campaign_file_path: str,
        data_dir_path: str,
        logger: ConsoleLogger,
    ) -> None:
        """Initialize manager with standard game/campaign paths."""
        super().__init__(
            game_install_dir_path=game_install_dir_path,
            campaign_file_path=campaign_file_path,
            data_dir_path=data_dir_path,
            logger=logger,
        )
        self.vehicle_entities: list[VehicleAppearanceEntity] = []

    def prepare_vehicle_entities(self) -> None:
        """Load and parse editable Entity blocks from extracted campaign data."""
        content = self._read_campaign_content()
        self.vehicle_entities = self._extract_vehicle_entities(content)

    def remove_vehicle_armor_damage(self, entity_id: str) -> bool:
        """Remove the full Armor section from selected Entity block.

        Returns True when an Armor section was removed.
        """
        updated = self._edit_entity_block(entity_id, self._remove_armor_from_block)
        if updated:
            self.logger.log(f"Removed Armor section for {entity_id}.")
            self.prepare_vehicle_entities()
        else:
            self.logger.log(f"No Armor section found for {entity_id}.")
        return updated

    def update_vehicle_enumerator(
        self,
        entity_id: str,
        number_value: str,
        digit_folder_value: str,
    ) -> bool:
        """Update number and digit_folder in existing Extender \"enumerator\" section.

        Returns True when enumerator values were updated.
        """
        normalized_number = self.normalize_enumerator_number(number_value)

        def _updater(block_text: str) -> tuple[str, bool]:
            if '{Extender "enumerator"' not in block_text:
                return block_text, False

            updated_text = NUMBER_PATTERN.sub(
                rf"\g<1>{normalized_number}\g<3>",
                block_text,
                count=1,
            )
            updated_text = DIGIT_FOLDER_PATTERN.sub(
                rf"\g<1>{digit_folder_value}\g<3>",
                updated_text,
                count=1,
            )
            return updated_text, updated_text != block_text

        updated = self._edit_entity_block(entity_id, _updater)
        if updated:
            self.logger.log(
                f"Updated enumerator for {entity_id}: number={normalized_number}, digit_folder={digit_folder_value}."
            )
            self.prepare_vehicle_entities()
        else:
            self.logger.log(f"No enumerator section found for {entity_id}.")
        return updated

    def normalize_enumerator_number(self, number_value: str) -> str:
        """Normalize user-provided enumerator number to a three-digit string."""
        stripped = number_value.strip()
        if not stripped.isdigit():
            raise ValueError("Enumerator number must contain only digits.")

        integer_value = int(stripped)
        if integer_value < 0 or integer_value > 999:
            raise ValueError("Enumerator number must be between 0 and 999.")

        return f"{integer_value:03d}"

    def save_changes(self) -> None:
        """Persist appearance edits back into the campaign save archive."""
        self.data_manager.create_campaign_file_backup()
        self.data_manager.create_campaign_status_file_backup()
        self.data_manager.save_campaign_file()

    def _read_campaign_content(self) -> str:
        with open(self.data_manager.campaign_data_file_path, "r", encoding="utf-8") as file:
            return file.read()

    def _write_campaign_content(self, content: str) -> None:
        with open(self.data_manager.campaign_data_file_path, "w", encoding="utf-8") as file:
            file.write(content)

    def _edit_entity_block(
        self,
        entity_id: str,
        updater: Callable[[str], tuple[str, bool]],
    ) -> bool:
        content = self._read_campaign_content()
        blocks = self._extract_entity_blocks(content)

        target_block = None
        for block in blocks:
            if block.entity_id == entity_id:
                target_block = block
                break

        if target_block is None:
            return False

        block_text = target_block.text
        updated_block_text, changed = updater(block_text)
        if not changed:
            return False

        updated_content = (
            content[: target_block.start_offset]
            + updated_block_text
            + content[target_block.end_offset :]
        )
        self._write_campaign_content(updated_content)
        return True

    def _extract_vehicle_entities(self, content: str) -> list[VehicleAppearanceEntity]:
        entities: list[VehicleAppearanceEntity] = []
        for block in self._extract_entity_blocks(content):
            block_text = block.text
            has_enumerator = '{Extender "enumerator"' in block_text
            number_match = NUMBER_PATTERN.search(block_text)
            digit_folder_match = DIGIT_FOLDER_PATTERN.search(block_text)
            entities.append(
                VehicleAppearanceEntity(
                    breed=block.breed,
                    entity_id=block.entity_id,
                    has_armor_section="{Armor" in block_text,
                    has_enumerator=has_enumerator,
                    number_value=number_match.group(2) if number_match else None,
                    digit_folder_value=(
                        digit_folder_match.group(2) if digit_folder_match else None
                    ),
                )
            )
        return entities

    def _extract_entity_blocks(self, content: str) -> list[EntityBlock]:
        blocks: list[EntityBlock] = []
        lines = content.splitlines(keepends=True)
        offsets: list[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line)

        index = 0
        while index < len(lines):
            line = lines[index]
            match = ENTITY_START_PATTERN.match(line)
            if not match:
                index += 1
                continue

            breed = match.group(1)
            entity_id = match.group(2)
            start_line = index

            depth = 0
            end_line = index
            while end_line < len(lines):
                current_line = lines[end_line]
                depth += current_line.count("{") - current_line.count("}")
                if depth == 0:
                    break
                end_line += 1

            start_offset = offsets[start_line]
            end_offset = offsets[end_line] + len(lines[end_line])
            text = "".join(lines[start_line : end_line + 1])
            blocks.append(
                EntityBlock(
                    breed=breed,
                    entity_id=entity_id,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    text=text,
                )
            )
            index = end_line + 1

        return blocks

    def _remove_armor_from_block(self, block_text: str) -> tuple[str, bool]:
        lines = block_text.splitlines(keepends=True)
        armor_start = -1
        for idx, line in enumerate(lines):
            if "{Armor" in line:
                armor_start = idx
                break

        if armor_start == -1:
            return block_text, False

        depth = 0
        armor_end = armor_start
        while armor_end < len(lines):
            current_line = lines[armor_end]
            depth += current_line.count("{") - current_line.count("}")
            if depth == 0:
                break
            armor_end += 1

        updated_lines = lines[:armor_start] + lines[armor_end + 1 :]
        return "".join(updated_lines), True