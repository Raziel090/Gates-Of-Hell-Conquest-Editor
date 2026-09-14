import unittest
from types import SimpleNamespace
from typing import get_type_hints

from src.entity_inventory import EntityInventory, GameItemInfo


class EntityInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory = EntityInventory(
            squad_id=1,
            entity_id="0x8000",
            entity_breed="human",
            inventory_entries=[],
            supplies=0,
            resources=0,
            fuel=0.0,
            knowledge_base=SimpleNamespace(logger=None),
        )

    def test_malformed_inventory_entry_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.inventory.convert_inventory_entry_to_game_item_info(
                '{item "weapon" {cell 1}}'
            )

    def test_prepare_inventory_item_entry_formats_expected_string(self) -> None:
        item_info = GameItemInfo(
            game_item_name="foo.bar",
            amount=3,
            cell_x=1,
            cell_y=2,
        )

        entry = self.inventory.prepare_inventory_item_entry(item_info, amount=3)

        self.assertIn('"foo" ', entry)
        self.assertIn('"bar" ', entry)
        self.assertIn("3 ", entry)
        self.assertIn("{cell 1 2}", entry)

    def test_find_inventory_space_for_item_declares_game_item_info_return_type(self) -> None:
        hints = get_type_hints(self.inventory.find_inventory_space_for_item)

        self.assertEqual(hints["return"], GameItemInfo)

    def test_fill_item_skips_full_stacks_and_fills_partial_stack(self) -> None:
        self.inventory.inventory_entries = [
            '\t{item "test" 5 {cell 0 0}}\n',
            '\t{item "test" 2 {cell 1 0}}\n',
        ]
        self.inventory.create_inventory_matrix = lambda: None

        filled_amount = self.inventory.fill_item_in_inventory(
            "test", max_amount=5, amount_to_add=3
        )

        self.assertEqual(filled_amount, 3)
        self.assertIn('"test" 5 {cell 1 0}', self.inventory.inventory_entries[1])


if __name__ == "__main__":
    unittest.main()
