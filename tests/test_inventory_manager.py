import tempfile
import unittest
from pathlib import Path

from src.game_file_parser import parse_game_file
from src.knowledge_base import KnowledgeBase
from src.knowledge_base import BreedItemInfo
from src.managers.inventory_manager import InventoryManager, _substitute_army_key_in_breed


class InventoryManagerRefactorTests(unittest.TestCase):
    def test_substitute_army_key_in_breed_replaces_army_segment_for_mp_breeds(self) -> None:
        breed = "mp/usa/mid/rifle"

        substituted_breed = _substitute_army_key_in_breed(breed, "ger")

        self.assertEqual(substituted_breed, "mp/ger/mid/rifle")

    def test_substitute_army_key_in_breed_leaves_non_mp_breeds_unchanged(self) -> None:
        breed = "tank"

        substituted_breed = _substitute_army_key_in_breed(breed, "ger")

        self.assertEqual(substituted_breed, breed)

    def test_standard_machinegun_does_not_match_heavy_machinegun_ammo(self) -> None:
        manager = InventoryManager.__new__(InventoryManager)
        heavy_machinegun_ammo = BreedItemInfo("ammo hmgun_usa", 300)

        ammo_type = manager._determine_ammo_type(
            item=heavy_machinegun_ammo,
            weapon_name="browning_m1919a4",
            weapon_type="mgun",
            inventory=[heavy_machinegun_ammo],
            index=0,
        )

        self.assertEqual(ammo_type, "")

    def test_parsed_inventory_entry_preserves_item_amount(self) -> None:
        knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
        knowledge_base.canonical_item_names = {"mgun_usa.belt.ammo"}
        inventory = parse_game_file('{inventory {item "ammo mgun_usa belt" 1250}}')
        item = inventory.find_descendants("item", kind="block")[0]

        item_info = knowledge_base.convert_breed_inventory_entry_to_game_item_info(item)

        self.assertEqual(item_info, BreedItemInfo("mgun_usa.belt.ammo", 1250))

    def test_game_file_inventory_extraction_handles_comments_and_whitespace(self) -> None:
        knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
        content = '''
{inventory
  {item "ammo mgun_usa belt" 1250} ; vehicle machine gun ammunition
  {item "ammo hmgun_usa" 300}
}
'''
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "vehicle.def"
            file_path.write_text(content, encoding="utf-8")

            entries = knowledge_base._get_entries_from_game_file(
                str(file_path), "inventory", "item"
            )

        self.assertEqual([entry.args for entry in entries], [
            ["ammo mgun_usa belt", "1250"],
            ["ammo hmgun_usa", "300"],
        ])


if __name__ == "__main__":
    unittest.main()
