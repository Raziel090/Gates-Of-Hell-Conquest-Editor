import unittest

from src.managers.inventory_manager import _substitute_army_key_in_breed


class InventoryManagerRefactorTests(unittest.TestCase):
    def test_substitute_army_key_in_breed_replaces_army_segment_for_mp_breeds(self) -> None:
        breed = "mp/usa/mid/rifle"

        substituted_breed = _substitute_army_key_in_breed(breed, "ger")

        self.assertEqual(substituted_breed, "mp/ger/mid/rifle")

    def test_substitute_army_key_in_breed_leaves_non_mp_breeds_unchanged(self) -> None:
        breed = "tank"

        substituted_breed = _substitute_army_key_in_breed(breed, "ger")

        self.assertEqual(substituted_breed, breed)


if __name__ == "__main__":
    unittest.main()
