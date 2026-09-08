import unittest

from src.knowledge_base import BreedItemInfo, KnowledgeBase, WeaponInfo
from src.managers.inventory_manager import (
    UNIT_CLASS_SOLDIER,
    UNIT_CLASS_VEHICLE,
    InventoryManager,
    _substitute_army_key_in_breed,
)


class _StubLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def log(self, message: str) -> None:
        self.messages.append(message)


def _make_inventory_manager(pickup_defaults: dict) -> InventoryManager:
    inventory_manager = InventoryManager.__new__(InventoryManager)
    inventory_manager.logger = _StubLogger()
    knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
    knowledge_base.pickup_ammo_defaults = pickup_defaults
    inventory_manager.knowledge_base = knowledge_base
    return inventory_manager


class InventoryManagerRefactorTests(unittest.TestCase):
    def test_substitute_army_key_in_breed_replaces_army_segment_for_mp_breeds(self) -> None:
        breed = "mp/usa/mid/rifle"

        substituted_breed = _substitute_army_key_in_breed(breed, "ger")

        self.assertEqual(substituted_breed, "mp/ger/mid/rifle")

    def test_substitute_army_key_in_breed_leaves_non_mp_breeds_unchanged(self) -> None:
        breed = "tank"

        substituted_breed = _substitute_army_key_in_breed(breed, "ger")

        self.assertEqual(substituted_breed, breed)

    def test_determine_vehicle_ammo_type_prefers_standard_mgun_ammo_for_browning_m19a4(self) -> None:
        inventory_manager = InventoryManager.__new__(InventoryManager)
        inventory = [
            BreedItemInfo(game_item_name="ammo hmgun_usa", amount=300, is_visible=True),
            BreedItemInfo(game_item_name="ammo mgun_usa belt", amount=1250, is_visible=True),
        ]

        ammo_type = inventory_manager._determine_vehicle_ammo_type(
            item=inventory[0],
            weapon_name="browning_m19a4",
            weapon_type="mgun",
            inventory=inventory,
            index=0,
        )

        self.assertEqual(ammo_type, "")

        ammo_type = inventory_manager._determine_vehicle_ammo_type(
            item=inventory[1],
            weapon_name="browning_m19a4",
            weapon_type="mgun",
            inventory=inventory,
            index=1,
        )

        self.assertEqual(ammo_type, "ammo mgun_usa belt")

    def test_determine_vehicle_ammo_type_prefers_heavy_hmg_ammo_for_browning_m2(self) -> None:
        inventory_manager = InventoryManager.__new__(InventoryManager)
        inventory = [
            BreedItemInfo(game_item_name="ammo mgun_usa belt", amount=1250, is_visible=True),
            BreedItemInfo(game_item_name="ammo hmgun_usa", amount=300, is_visible=True),
        ]

        ammo_type = inventory_manager._determine_vehicle_ammo_type(
            item=inventory[0],
            weapon_name="browning_m2",
            weapon_type="mgun",
            inventory=inventory,
            index=0,
        )

        self.assertEqual(ammo_type, "")

        ammo_type = inventory_manager._determine_vehicle_ammo_type(
            item=inventory[1],
            weapon_name="browning_m2",
            weapon_type="mgun",
            inventory=inventory,
            index=1,
        )

        self.assertEqual(ammo_type, "ammo hmgun_usa")


class PickupAmmoDefaultsTests(unittest.TestCase):
    def test_compute_pickup_ammo_defaults_uses_median_per_unit_class(self) -> None:
        knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
        knowledge_base.item_block_sizes = {}
        knowledge_base.breeds_inventories = {
            "mp/ger/mid/mgun_1": [
                BreedItemInfo(game_item_name="mgun_ger.belt.ammo", amount=250),
            ],
            "mp/ger/mid/mgun_2": [
                BreedItemInfo(game_item_name="mgun_ger.belt.ammo", amount=500),
            ],
            "mp/ger/mid/mgun_3": [
                BreedItemInfo(game_item_name="mgun_ger.belt.ammo", amount=300),
            ],
        }
        knowledge_base.vehicle_inventories = {
            "some_halftrack": [
                BreedItemInfo(game_item_name="mgun_ger.belt.ammo", amount=4250),
            ],
        }

        defaults = knowledge_base._compute_pickup_ammo_defaults()

        self.assertEqual(defaults["soldier"]["mgun_ger.belt.ammo"], 300)
        self.assertEqual(defaults["vehicle"]["mgun_ger.belt.ammo"], 4250)

    def test_compute_pickup_ammo_defaults_ignores_non_ammo_items(self) -> None:
        knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
        knowledge_base.item_block_sizes = {}
        knowledge_base.breeds_inventories = {
            "mp/ger/mid/rifleman_1": [
                BreedItemInfo(game_item_name="shovel_ger", amount=1),
                BreedItemInfo(game_item_name="kar98k.ammo", amount=60),
            ],
        }
        knowledge_base.vehicle_inventories = {}

        defaults = knowledge_base._compute_pickup_ammo_defaults()

        self.assertNotIn("shovel_ger", defaults["soldier"])
        self.assertEqual(defaults["soldier"]["kar98k.ammo"], 60)
        self.assertEqual(defaults["vehicle"], {})

    def test_round_to_magazine_size_never_returns_less_than_one_stack(self) -> None:
        knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
        knowledge_base.item_block_sizes = {"nbks.grenade": "10"}

        self.assertEqual(knowledge_base._round_to_magazine_size("nbks.grenade", 3), 10)
        self.assertEqual(knowledge_base._round_to_magazine_size("nbks.grenade", 26), 30)
        self.assertEqual(knowledge_base._round_to_magazine_size("unknown.ammo", 7), 7)


class ResolvePickupAmmoTests(unittest.TestCase):
    def test_resolve_pickup_ammo_matches_mg_family_for_non_template_weapon(self) -> None:
        inventory_manager = _make_inventory_manager(
            {
                UNIT_CLASS_SOLDIER: {"mgun_usa.belt.ammo": 250},
                UNIT_CLASS_VEHICLE: {
                    "hmgun_usa.ammo": 300,
                    "mgun_usa.belt.ammo": 4250,
                },
            }
        )

        resolved = inventory_manager._resolve_pickup_ammo(
            WeaponInfo(weapon_name="browning_m19a4", weapon_type="stuff\\mgun"),
            UNIT_CLASS_VEHICLE,
        )

        self.assertIsNotNone(resolved)
        assert resolved is not None
        self.assertEqual(resolved.game_item_name, "mgun_usa.belt.ammo")
        self.assertEqual(resolved.amount, 4250)

    def test_resolve_pickup_ammo_prefers_base_variant_over_api_variant(self) -> None:
        inventory_manager = _make_inventory_manager(
            {
                UNIT_CLASS_SOLDIER: {},
                UNIT_CLASS_VEHICLE: {
                    "hmgun_usa.ammo": 300,
                    "hmgun_usa.api.ammo": 500,
                },
            }
        )

        resolved = inventory_manager._resolve_pickup_ammo(
            WeaponInfo(weapon_name="browning_m2", weapon_type="stuff\\mgun"),
            UNIT_CLASS_VEHICLE,
        )

        self.assertIsNotNone(resolved)
        assert resolved is not None
        self.assertEqual(resolved.game_item_name, "hmgun_usa.ammo")
        self.assertEqual(resolved.amount, 300)

    def test_resolve_pickup_ammo_returns_none_for_ambiguous_family(self) -> None:
        inventory_manager = _make_inventory_manager(
            {
                UNIT_CLASS_SOLDIER: {},
                UNIT_CLASS_VEHICLE: {
                    "hmgun_rus.ammo": 300,
                    "hmgun_ger.ammo": 500,
                },
            }
        )

        resolved = inventory_manager._resolve_pickup_ammo(
            WeaponInfo(weapon_name="browning_m2", weapon_type="stuff\\mgun"),
            UNIT_CLASS_VEHICLE,
        )

        self.assertIsNone(resolved)

    def test_resolve_pickup_ammo_returns_none_when_table_is_empty(self) -> None:
        inventory_manager = _make_inventory_manager(
            {UNIT_CLASS_SOLDIER: {}, UNIT_CLASS_VEHICLE: {}}
        )

        resolved = inventory_manager._resolve_pickup_ammo(
            WeaponInfo(weapon_name="browning_m19a4", weapon_type="stuff\\mgun"),
            UNIT_CLASS_VEHICLE,
        )

        self.assertIsNone(resolved)


if __name__ == "__main__":
    unittest.main()
