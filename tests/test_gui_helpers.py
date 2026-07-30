import unittest

from src.gui.inventory_action_controller import InventoryActionController
from src.gui.layout_utils import resolve_target_squad_id
from src.gui.unit_action_controller import UnitActionController
from src.gui.unit_selection_controller import UnitSelectionController


class GuiLayoutHelperTests(unittest.TestCase):
    def test_resolve_target_squad_id_offsets_selection_after_base_squad(self) -> None:
        self.assertEqual(resolve_target_squad_id(1, 1), 2)
        self.assertEqual(resolve_target_squad_id(2, 2), 3)

    def test_resolve_target_squad_id_leaves_selection_unchanged_before_base_squad(self) -> None:
        self.assertEqual(resolve_target_squad_id(0, 2), 0)
        self.assertEqual(resolve_target_squad_id(1, 2), 1)

    def test_selection_controller_filters_out_the_base_squad_from_target_options(self) -> None:
        controller = UnitSelectionController()
        squad_names = ["Alpha", "Bravo", "Charlie"]

        self.assertEqual(controller.build_target_squad_names(squad_names, 1), ["Alpha", "Charlie"])

    def test_action_controller_resolves_effective_target_squad_ids(self) -> None:
        controller = UnitActionController()

        self.assertEqual(controller.resolve_effective_target_squad_id(1, 0), 2)
        self.assertEqual(controller.resolve_effective_target_squad_id(0, 2), 0)

    def test_inventory_action_controller_formats_inventory_details(self) -> None:
        controller = InventoryActionController()

        self.assertEqual(
            controller.format_inventory_details({"ammo": 10, "medkit": 2}),
            "ammo: 10\nmedkit: 2",
        )


if __name__ == "__main__":
    unittest.main()
