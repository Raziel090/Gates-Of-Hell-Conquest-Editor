import unittest
from types import SimpleNamespace

from src.knowledge_base import BreedItemInfo
from src.managers.inventory_manager import InventoryManager, _substitute_army_key_in_breed


class InventoryManagerRefactorTests(unittest.TestCase):
    def _create_manager_with_refill_data(self) -> InventoryManager:
        manager = InventoryManager.__new__(InventoryManager)
        manager.logger = SimpleNamespace(log=lambda message: None)
        manager.knowledge_base = SimpleNamespace(
            weapons_list=[],
            item_weights={"test_item": 2.0},
            item_block_sizes={"test_item": "1"},
            campaign_status_info=SimpleNamespace(ap=100.0),
        )
        return manager

    def _create_full_inventory(self) -> SimpleNamespace:
        return SimpleNamespace(
            entity_id="0x8000",
            item_counts={},
            add_item_to_inventory=lambda item_name, amount: False,
            fill_item_in_inventory=lambda item_name, **kwargs: 0,
            count_items_in_inventory=lambda: None,
        )

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

    def test_refill_equipment_does_not_charge_when_inventory_is_full(self) -> None:
        manager = self._create_manager_with_refill_data()

        manager.refill_equipment(
            self._create_full_inventory(), [BreedItemInfo("test_item", 2)]
        )

        self.assertEqual(manager.knowledge_base.campaign_status_info.ap, 100.0)

    def test_ammo_refills_do_not_charge_when_inventory_is_full(self) -> None:
        manager = self._create_manager_with_refill_data()
        full_inventory = self._create_full_inventory()

        manager._refill_ammo_item(full_inventory, BreedItemInfo("test_item", 2))
        manager._refill_vehicle_standard_ammo(
            full_inventory, BreedItemInfo("test_item", 2)
        )

        self.assertEqual(manager.knowledge_base.campaign_status_info.ap, 100.0)

    def test_ammo_refill_uses_partial_stack_before_reporting_full_inventory(self) -> None:
        manager = self._create_manager_with_refill_data()
        manager.knowledge_base.item_block_sizes["test_item"] = "5"
        messages: list[str] = []
        manager.logger = SimpleNamespace(log=messages.append)
        fill_results = iter([3, 0])
        inventory = SimpleNamespace(
            entity_id="0x8000",
            item_counts={"test_item": 17},
            fill_item_in_inventory=lambda item_name, **kwargs: next(fill_results),
            add_item_to_inventory=lambda item_name, amount: False,
        )

        manager._refill_ammo_item(inventory, BreedItemInfo("test_item", 25))

        self.assertEqual(manager.knowledge_base.campaign_status_info.ap, 94.0)
        self.assertTrue(
            any("Could not add 5 of test_item" in message for message in messages)
        )

if __name__ == "__main__":
    unittest.main()
