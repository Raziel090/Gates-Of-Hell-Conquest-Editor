import unittest

from src.knowledge_base import KnowledgeBase


class _StubLogger:
    def log(self, message: str) -> None:
        pass


def _make_kb(canonical_names: set[str]) -> KnowledgeBase:
    knowledge_base = KnowledgeBase.__new__(KnowledgeBase)
    knowledge_base.logger = _StubLogger()
    knowledge_base.canonical_item_names = canonical_names
    return knowledge_base


class ItemNameNormalizationTests(unittest.TestCase):
    def test_mgun_usa_without_belt_maps_to_belt_variant(self) -> None:
        kb = _make_kb({"mgun_usa.belt.ammo"})

        self.assertEqual(kb.get_correct_item_name("ammo mgun_usa"), "mgun_usa.belt.ammo")

    def test_mgun_usa_belt_reorders_normally(self) -> None:
        kb = _make_kb({"mgun_usa.belt.ammo"})

        self.assertEqual(
            kb.get_correct_item_name("ammo mgun_usa belt"), "mgun_usa.belt.ammo"
        )

    def test_hmgun_reorders_qualifier_before_ammo(self) -> None:
        kb = _make_kb({"hmgun_usa.ammo"})

        self.assertEqual(kb.get_correct_item_name("ammo hmgun_usa"), "hmgun_usa.ammo")

    def test_usa_grenade_reorders_to_canonical(self) -> None:
        # The usa_grenade reorder returns the joined reorder directly (no .ammo
        # suffix), matching the original behavior.
        kb = _make_kb({"mk2.usa_grenade.he"})

        self.assertEqual(
            kb.get_correct_item_name("mk2 usa_grenade he"), "mk2.usa_grenade.he"
        )

    def test_bullet_reorders_qualifier_before_ammo(self) -> None:
        kb = _make_kb({"bulletusa_37.apcbc.ammo"})

        self.assertEqual(
            kb.get_correct_item_name("ammo bulletusa_37 apcbc"),
            "bulletusa_37.apcbc.ammo",
        )

    def test_mortar_without_matching_item_is_not_suffixed(self) -> None:
        # The real item is "230mm_spigot_mortar" with no .ammo file, so the
        # ".ammo" suffix must not be appended.
        kb = _make_kb({"230mm_spigot_mortar"})

        self.assertEqual(
            kb.get_correct_item_name("230mm_spigot_mortar"), "230mm_spigot_mortar"
        )

    def test_bullet_with_matching_ammo_item_is_suffixed(self) -> None:
        # A bare bullet name whose .ammo item exists gains the suffix.
        kb = _make_kb({"bulletrus_76.ammo"})

        self.assertEqual(kb.get_correct_item_name("bulletrus_76"), "bulletrus_76.ammo")

    def test_bullet_without_matching_ammo_item_is_not_suffixed(self) -> None:
        # The real item is the bare name (no .ammo file), so no suffix is added.
        kb = _make_kb({"bulletrus_76"})

        self.assertEqual(kb.get_correct_item_name("bulletrus_76"), "bulletrus_76")

    def test_bullet_without_canonical_ammo_file_is_not_suffixed(self) -> None:
        # With the real item set populated, a bare bullet name whose .ammo file
        # does not exist falls back to the plain join rather than a wrong name.
        kb = _make_kb({"bulletrus_76.ammo", "hmgun_usa.ammo"})

        self.assertEqual(kb.get_correct_item_name("bulletrus_305"), "bulletrus_305")

    def test_plain_unknown_name_falls_back_to_join(self) -> None:
        # A name with no ammo/bullet/mgun keyword always returns the plain join.
        kb = _make_kb(set())

        self.assertEqual(kb.get_correct_item_name("repair_kit"), "repair_kit")

    def test_plain_weapon_name_unchanged(self) -> None:
        kb = _make_kb({"browning_m2"})

        self.assertEqual(kb.get_correct_item_name("browning_m2"), "browning_m2")

    def test_empty_name_returned_as_is(self) -> None:
        kb = _make_kb(set())

        self.assertEqual(kb.get_correct_item_name(""), "")


if __name__ == "__main__":
    unittest.main()
