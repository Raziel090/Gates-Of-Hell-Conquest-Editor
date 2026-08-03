import tempfile
import unittest
from pathlib import Path

from src.managers.vehicle_appearance_manager import VehicleAppearanceManager


class _DummyLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)


class _DummyDataManager:
    def __init__(self, campaign_data_file_path: Path) -> None:
        self.campaign_data_file_path = campaign_data_file_path


class VehicleAppearanceManagerTests(unittest.TestCase):
    def _create_manager(self, campaign_data_file_path: Path) -> VehicleAppearanceManager:
        manager = VehicleAppearanceManager.__new__(VehicleAppearanceManager)
        manager.logger = _DummyLogger()
        manager.data_manager = _DummyDataManager(campaign_data_file_path)
        manager.vehicle_entities = []
        return manager

    def test_remove_vehicle_armor_damage_removes_full_armor_section(self) -> None:
        content = (
            '{Entity "tank" 0x1111\n'
            '\t{Position 1 2}\n'
            '\t{Armor\n'
            '\t\t{wounds\n'
            '\t\t\t{damage "body" 0.1 1}\n'
            '\t\t}\n'
            '\t}\n'
            '\t{Player 0}\n'
            '}\n'
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            campaign_path = Path(temp_dir) / "campaign.scn"
            campaign_path.write_text(content, encoding="utf-8")

            manager = self._create_manager(campaign_path)
            updated = manager.remove_vehicle_armor_damage("0x1111")

            saved_content = campaign_path.read_text(encoding="utf-8")
            self.assertTrue(updated)
            self.assertNotIn("{Armor", saved_content)
            self.assertIn('{Entity "tank" 0x1111', saved_content)

    def test_update_vehicle_enumerator_updates_number_and_folder(self) -> None:
        content = (
            '{Entity "tank" 0x1111\n'
            '\t{Extender "enumerator"\n'
            '\t\t{number 7}\n'
            '\t\t{digit_folder "ger"}\n'
            '\t}\n'
            '}\n'
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            campaign_path = Path(temp_dir) / "campaign.scn"
            campaign_path.write_text(content, encoding="utf-8")

            manager = self._create_manager(campaign_path)
            updated = manager.update_vehicle_enumerator("0x1111", "7", "ru1")

            saved_content = campaign_path.read_text(encoding="utf-8")
            self.assertTrue(updated)
            self.assertIn("{number 007}", saved_content)
            self.assertIn('{digit_folder "ru1"}', saved_content)

    def test_update_vehicle_enumerator_skips_when_not_present(self) -> None:
        content = (
            '{Entity "tank" 0x1111\n'
            '\t{Player 0}\n'
            '}\n'
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            campaign_path = Path(temp_dir) / "campaign.scn"
            campaign_path.write_text(content, encoding="utf-8")

            manager = self._create_manager(campaign_path)
            updated = manager.update_vehicle_enumerator("0x1111", "321", "ger")

            saved_content = campaign_path.read_text(encoding="utf-8")
            self.assertFalse(updated)
            self.assertNotIn("{number 321}", saved_content)


if __name__ == "__main__":
    unittest.main()