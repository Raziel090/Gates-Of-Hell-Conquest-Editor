"""Inventory management for squad members and equipment."""

import random
from difflib import SequenceMatcher
import re

from src.managers.game_manager import GameManager
from src.console_logger import ConsoleLogger
from src.entity_inventory import EntityInventory
from src.knowledge_base import (
    BreedItemInfo,
    WeaponInfo,
)

UNITS_SUBSTITUTIONS = {
    "mp/usa/mid/crew": "mp/ger/mid/artilleryman",
    "mp/usa/mid/82nd_crew": "mp/ger/mid/artilleryman",
    "mp/usa/mid/rifle": "mp/ger/mid/rifleman_1",
    "mp/usa/mid/driver": "mp/ger/mid/rifleman_1",
    "mp/usa/mid/driver_smg": "mp/ger/mid/rifleman_1",
    "mp/usa/mid/cav_driver": "mp/ger/mid/rifleman_1",
    "mp/usa/mid/cav_gunner": "mp/ger/mid/rifleman_1",
    "mp/usa/late/cav_driver": "mp/ger/late/rifleman_1",
    "mp/usa/late/cav_gunner": "mp/ger/late/rifleman_1",
    "mp/usa/mid/ar1_driver": "mp/ger/mid/smg_1",
    "mp/usa/mid/ar1_rifle": "mp/ger/mid/rifleman_1",
    "mp/usa/mid/vehicle_crew_m1": "mp/ger/mid/tankman",
    "mp/usa/mid/vehicle_com": "mp/ger/mid/tank_commander",
    "mp/usa/mid/vehicle_crew": "mp/ger/mid/tankman",
    "mp/usa/mid/engineer_builder": "mp/ger/mid/engineer_1",
    "mp/usa/late/tankman_m3": "mp/ger/mid/tankman",
    "mp/usa/late/tank_com_m3": "mp/ger/mid/tank_commander",
    "mp/usa/late/tankman_m1": "mp/ger/mid/tankman",
    "mp/usa/late/tank_com_m1": "mp/ger/mid/tank_commander",
    "mp/fin/early/rifleman": "mp/ger/early/rifleman_1",
    "mp/fin/mid/rifleman": "mp/ger/mid/rifleman_1",
    "mp/fin/late/rifleman": "mp/ger/late/rifleman_1",
    "mp/fin/mid/engineer_builder": "mp/ger/mid/engineer_1",
    "mp/fin/late/engineer_builder": "mp/ger/late/engineer_1",
    "mp/fin/mid/tankman_vet": "mp/ger/mid/tankman",
    "mp/fin/mid/tank_commander_vet": "mp/ger/mid/tank_commander",
    "mp/eng/early/crew": "mp/ger/early/rifleman_1",
    "mp/eng/mid/crew": "mp/ger/mid/rifleman_1",
    "mp/eng/late/crew": "mp/ger/late/rifleman_1",
    "mp/eng/early/driver": "mp/ger/early/rifleman_1",
    "mp/eng/mid/driver": "mp/ger/mid/rifleman_1",
    "mp/eng/late/driver": "mp/ger/late/rifleman_1",
    "mp/eng/early/r_eng_builder": "mp/ger/early/engineer_1",
    "mp/eng/mid/r_eng_builder": "mp/ger/mid/engineer_1",
    "mp/eng/late/r_eng_builder": "mp/ger/late/engineer_1",
    "mp/eng/early/vehicle_crew": "mp/ger/early/tankman",
    "mp/eng/mid/vehicle_crew": "mp/ger/mid/tankman",
    "mp/eng/late/vehicle_crew": "mp/ger/late/tankman",
    "mp/eng/early/vehicle_com_sgt": "mp/ger/early/tank_commander",
    "mp/eng/mid/vehicle_com_sgt": "mp/ger/mid/tank_commander",
    "mp/eng/late/vehicle_com_sgt": "mp/ger/late/tank_commander",
    "mp/eng/early/vehicle_com_cpl": "mp/ger/early/tank_commander",
    "mp/eng/mid/vehicle_com_cpl": "mp/ger/mid/tank_commander",
    "mp/eng/late/vehicle_com_cpl": "mp/ger/late/tank_commander",
    "mp/ger/mid/rifleman_1": "mp/usa/mid/rifle",
    "mp/ger/mid/mgun_2": "mp/usa/mid/mg_crew_asst",
    "mp/ger/mid/engineer_1": "mp/usa/mid/engineer_builder",
    "mp/ger/mid/engineer_2": "mp/usa/mid/engineer_builder",
    "mp/ger/mid/rifleman_1": "mp/usa/mid/rifle",
    "mp/ger/mid/recon_rifle": "mp/usa/mid/rifle",
    "mp/ger/mid/tankman_stug": "mp/usa/mid/tankman",
    "mp/ger/mid/tank_commander_stug": "mp/usa/mid/tank_commander",
    "mp/ger/mid/tankman_ace": "mp/usa/mid/tankman",
    "mp/ger/mid/tank_commander_ace": "mp/usa/mid/tank_commander",
    "mp/ger/mid/tankman_pzjag": "mp/usa/mid/tankman",
    "mp/ger/mid/tank_commander_pzjag": "mp/usa/mid/tank_commander",
    "mp/ger/mid/tankman_scout": "mp/usa/mid/tankman",
    "mp/ger/mid/tank_commander_scout": "mp/usa/mid/tank_commander",
    "mp/ger/late/rifleman_1": "mp/usa/late/rifle",
    "mp/ger/late/mgun_2": "mp/usa/late/mg_crew_asst",
    "mp/ger/late/engineer_1": "mp/usa/late/engineer_builder",
    "mp/ger/late/engineer_2": "mp/usa/late/engineer_builder",
    "mp/ger/late/rifleman_1": "mp/usa/late/rifle",
    "mp/ger/late/recon_rifle": "mp/usa/late/rifle",
    "mp/ger/late/tankman_stug": "mp/usa/late/tankman",
    "mp/ger/late/tank_commander_stug": "mp/usa/late/tank_commander",
    "mp/ger/late/tankman_ace": "mp/usa/late/tankman",
    "mp/ger/late/tank_commander_ace": "mp/usa/late/tank_commander",
    "mp/ger/late/tankman_pzjag": "mp/usa/late/tankman",
    "mp/ger/late/tank_commander_pzjag": "mp/usa/late/tank_commander",
    "mp/ger/late/tankman_scout": "mp/usa/late/tankman",
    "mp/ger/late/tank_commander_scout": "mp/usa/late/tank_commander",
    "mp/ger/early/rifleman_1": "mp/eng/early/rifle",
    "mp/ger/early/mgun_2": "mp/eng/early/mg_crew_asst",
    "mp/ger/early/engineer_1": "mp/eng/early/r_engineer_builder",
    "mp/ger/early/engineer_2": "mp/eng/early/r_engineer_builder",
    "mp/ger/early/rifleman_1": "mp/eng/early/rifle",
    "mp/ger/early/recon_rifle": "mp/eng/early/rifle",
    "mp/ger/early/tankman_stug": "mp/eng/early/tankman",
    "mp/ger/early/tank_commander_stug": "mp/eng/early/tank_commander",
    "mp/ger/mid/rifleman_1": "mp/eng/mid/rifle",
    "mp/ger/mid/mgun_2": "mp/eng/mid/mg_crew_asst",
    "mp/ger/mid/engineer_1": "mp/eng/mid/r_engineer_builder",
    "mp/ger/mid/engineer_2": "mp/eng/mid/r_engineer_builder",
    "mp/ger/mid/rifleman_1": "mp/eng/mid/rifle",
    "mp/ger/mid/recon_rifle": "mp/eng/mid/rifle",
    "mp/ger/mid/tankman_stug": "mp/eng/mid/tankman",
    "mp/ger/mid/tank_commander_stug": "mp/eng/mid/tank_commander",
    "mp/ger/mid/tankman_ace": "mp/eng/mid/tankman",
    "mp/ger/mid/tank_commander_ace": "mp/eng/mid/tank_commander",
    "mp/ger/mid/tankman_pzjag": "mp/eng/mid/tankman",
    "mp/ger/mid/tank_commander_pzjag": "mp/eng/mid/tank_commander",
    "mp/ger/mid/tankman_scout": "mp/eng/mid/tankman",
    "mp/ger/mid/tank_commander_scout": "mp/eng/mid/tank_commander",
    "mp/ger/late/rifleman_1": "mp/eng/late/rifle",
    "mp/ger/late/mgun_2": "mp/eng/late/mg_crew_asst",
    "mp/ger/late/engineer_1": "mp/eng/late/r_engineer_builder",
    "mp/ger/late/engineer_2": "mp/eng/late/r_engineer_builder",
    "mp/ger/late/rifleman_1": "mp/eng/late/rifle",
    "mp/ger/late/recon_rifle": "mp/eng/late/rifle",
    "mp/ger/late/tankman_stug": "mp/eng/late/tankman",
    "mp/ger/late/tank_commander_stug": "mp/eng/late/tank_commander",
    "mp/ger/late/tankman_ace": "mp/eng/late/tankman",
    "mp/ger/late/tank_commander_ace": "mp/eng/late/tank_commander",
    "mp/ger/late/tankman_pzjag": "mp/eng/late/tankman",
    "mp/ger/late/tank_commander_pzjag": "mp/eng/late/tank_commander",
    "mp/ger/late/tankman_scout": "mp/eng/late/tankman",
    "mp/ger/late/tank_commander_scout": "mp/eng/late/tank_commander",
}


# Constants for common strings
# Unit types
UNIT_TYPE_HUMAN = "Human"
UNIT_TYPE_ENTITY = "Entity"
PROPERTY_HUMAN = "human"

# Weapon/ammo related strings
BROWNING_M2_WEAPON = "browning_m2"
HMGUN_USA_AMMO = "hmgun_usa"
MP_PREFIX = "mp/"
UNDERSCORE_SEPARATOR = "_"

# Unit classes used for pickup ammo defaults
UNIT_CLASS_SOLDIER = "soldier"
UNIT_CLASS_VEHICLE = "vehicle"

# ID constants
DECEASED_MEMBER_ID = "0xffffffff"
HEX_PREFIX = "0x"

# Log message templates
LOG_WEAPON_ADDED = "Added weapon to inventory: {item_name} of {entity_id}."
LOG_ITEM_ADDED = (
    "Added {amount} of {item_name} for {cost} AP to inventory of {entity_id}."
)
LOG_MISSING_WEAPONS_ADDED = "Added missing weapons to {entity_id} inventory"
LOG_ITEM_TO_INVENTORY = "Added {amount} of {item_name} to inventory of {entity_id}."
LOG_NEW_UNIT_ENTRY = "Added new unit entry to squad {squad_name}: {unit_entry}"
LOG_NEW_SQUAD_MEMBERS = (
    "Added {count} new squad members to squad {squad_name} for {cost} MP."
)
LOG_RESOURCES_ADDED = "Total {amount} resources added to {entity_id} for {cost} AP."
LOG_SUPPLIES_ADDED = "Total {amount} supplies added to {entity_id} for {cost} AP."
LOG_FUEL_ADDED = "Total {amount} fuel added to {entity_id} for {cost} AP."
LOG_REFILLED_AMMO = "Refilled ammunition for {weapon_name} in {entity_id} inventory"
LOG_NOT_ENOUGH_AP_ITEM = "Not enough AP to refill {item_type} in {entity_id} inventory."
LOG_NOT_ENOUGH_MP_UNIT = "Not enough MP to add {breed} to squad {squad_name}!"

# Numeric constants
SIMILARITY_THRESHOLD = 0.7
HEX_RANGE_MIN = 0x8000
HEX_RANGE_MAX = 0xFFFF
MAX_RESOURCES = 10
RESOURCE_MULTIPLIER = 10


def _substitute_army_key_in_breed(breed: str, army: str) -> str:
    """Replace the army segment in an MP breed path with the requested faction."""
    if MP_PREFIX in breed:
        breed_split = breed.split("/")
        breed_split[1] = army
        return "/".join(breed_split)
    return breed


class InventoryManager(GameManager):
    """Manage squad member inventories and equipment refills."""

    def __init__(
        self,
        game_install_dir_path: str,
        campaign_file_path: str,
        data_dir_path: str,
        logger: ConsoleLogger,
    ) -> None:
        """Initialize InventoryManager with game paths and logger.

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

        self.squad_members_ids: list[str] = []
        self.new_unit_entries: list[str] = []
        self.new_units_resupplied_squads: list[int] = []

    def prepare_squads_and_inventories(self, keep_deceased_members: bool = False) -> None:
        """Prepare squad data and collect all member IDs."""
        super().prepare_squads_and_inventories(
            keep_deceased_members=keep_deceased_members
        )
        self.squad_members_ids = self.get_all_squad_members_ids()

    def refill_human_squad_member_inventory(
        self, squad_member_inventory: EntityInventory
    ) -> None:
        """Refill human squad member with weapons, equipment and ammunition.

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
        """
        squad_member_inventory.create_inventory_matrix()
        squad_member_inventory.count_items_in_inventory()
        squad_member_breed = squad_member_inventory.entity_breed

        weapons_in_inventory = squad_member_inventory.find_gun_entries_in_inventory()
        weapons = [weapon_info.weapon_name for weapon_info in weapons_in_inventory]

        standard_inventory: list[BreedItemInfo] = (
            self.knowledge_base.breeds_inventories[squad_member_breed]
        )

        if not weapons:
            self.refill_weapons(
                squad_member_inventory=squad_member_inventory,
                standard_inventory=standard_inventory,
            )
            weapons_in_inventory = (
                squad_member_inventory.find_gun_entries_in_inventory()
            )

        self.refill_equipment(
            squad_member_inventory=squad_member_inventory,
            standard_inventory=standard_inventory,
        )

        self.refill_ammunition(
            squad_member_inventory=squad_member_inventory,
            standard_inventory=standard_inventory,
            weapons_in_inventory=weapons_in_inventory,
        )

        if squad_member_inventory.resources >= 0:
            self.refill_supplies_resources(
                squad_member_inventory=squad_member_inventory
            )

    def refill_vehicle_squad_member_inventory(
        self, squad_member_inventory: EntityInventory
    ) -> None:
        """Refill vehicle inventory with equipment, ammunition and fuel.

        Args:
            squad_member_inventory (EntityInventory): The vehicle's inventory
        """
        squad_member_inventory.create_inventory_matrix()
        squad_member_inventory.count_items_in_inventory()
        squad_member_breed = squad_member_inventory.entity_breed

        standard_inventory: list[BreedItemInfo] = (
            self.knowledge_base.vehicle_inventories[squad_member_breed]
        )

        self.refill_equipment(
            squad_member_inventory=squad_member_inventory,
            standard_inventory=standard_inventory,
        )

        self.refill_vehicle_ammunition(
            squad_member_inventory=squad_member_inventory,
            standard_inventory=standard_inventory,
        )

        if squad_member_inventory.supplies > 0:
            self.refill_supplies(squad_member_inventory=squad_member_inventory)

        if squad_member_inventory.fuel >= 0:
            self.refill_fuel(squad_member_inventory=squad_member_inventory)

    def refill_squad_member_inventory(
        self, squad_id: int, squad_member_id: str
    ) -> None:
        """Refill specific squad member's inventory based on type.

        Args:
            squad_id (int): The squad identifier
            squad_member_id (str): The squad member identifier
        """
        for squad_inventory in self.squads_inventories:
            if squad_inventory.squad_id == squad_id:
                squad_member_inventory: EntityInventory = squad_inventory.inventories[
                    squad_member_id
                ]
                squad_member_breed = squad_member_inventory.entity_breed
                squad_member_property = self.knowledge_base.vehicles_properties.get(
                    squad_member_breed, PROPERTY_HUMAN
                )
                if squad_member_property == PROPERTY_HUMAN:
                    self.refill_human_squad_member_inventory(
                        squad_member_inventory=squad_member_inventory,
                    )
                else:
                    self.refill_vehicle_squad_member_inventory(
                        squad_member_inventory=squad_member_inventory,
                    )
                break

    def refill_weapons(
        self,
        squad_member_inventory: EntityInventory,
        standard_inventory: list[BreedItemInfo],
    ) -> None:
        """Refill squad member with standard weapons.

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
            standard_inventory (list[BreedItemInfo]): Standard inventory items
        """
        for item in standard_inventory:
            item_name = item.game_item_name
            if not item.is_visible:
                continue

            if item_name not in self.knowledge_base.weapons_list:
                continue

            campaign_status_info = self.knowledge_base.campaign_status_info
            if campaign_status_info is None:
                self.logger.log("Campaign status information is not initialized.")
                return

            item_refill_cost = self.knowledge_base.item_weights[item_name]
            if campaign_status_info.ap - item_refill_cost < 0:
                self.logger.log(
                    f"Not enough AP to refill {item_name} in {squad_member_inventory.entity_id} inventory."
                )
                continue

            item_amount = 1
            added_item = squad_member_inventory.add_item_to_inventory(
                item_name, amount=item_amount
            )
            if added_item:
                campaign_status_info.ap -= item_refill_cost

                self.logger.log(
                    LOG_WEAPON_ADDED.format(
                        item_name=item_name, entity_id=squad_member_inventory.entity_id
                    )
                )

    def refill_equipment(
        self,
        squad_member_inventory: EntityInventory,
        standard_inventory: list[BreedItemInfo],
    ) -> None:
        """Refill squad member with standard equipment items.

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
            standard_inventory (list[BreedItemInfo]): Standard inventory items
        """
        for item in standard_inventory:
            item_name = item.game_item_name
            amount = item.amount

            if item_name in self.knowledge_base.weapons_list:
                continue
            if "ammo" in item_name or "bullet" in item_name:
                continue
            if not item.is_visible:
                continue
            item_counts = squad_member_inventory.item_counts or {}
            squad_member_inventory_amount = item_counts.get(item_name, 0)

            if squad_member_inventory_amount < amount:
                item_amount = amount - squad_member_inventory_amount
                item_refill_cost = (
                    self.knowledge_base.item_weights[item_name] * item_amount
                )
                campaign_status_info = self.knowledge_base.campaign_status_info
                if campaign_status_info is None:
                    self.logger.log("Campaign status information is not initialized.")
                    return

                if campaign_status_info.ap - item_refill_cost < 0:
                    self.logger.log(
                        f"Not enough AP to refill {item_name} in {squad_member_inventory.entity_id} inventory."
                    )
                    continue

                item_block_size = self.knowledge_base.item_block_sizes.get(
                    item_name, "1"
                )
                item_block_size = int(item_block_size)

                in_game_item_full_stacks = item_amount // item_block_size
                in_game_item_remainder = item_amount % item_block_size
                added_item = False
                for _ in range(in_game_item_full_stacks):
                    added_item = squad_member_inventory.add_item_to_inventory(
                        item_name, amount=item_block_size
                    )
                if in_game_item_remainder > 0:
                    added_item = squad_member_inventory.add_item_to_inventory(
                        item_name, amount=in_game_item_remainder
                    )

                campaign_status_info.ap -= item_refill_cost

                if added_item:
                    self.logger.log(
                        LOG_ITEM_ADDED.format(
                            amount=item_amount,
                            item_name=item_name,
                            cost=item_refill_cost,
                            entity_id=squad_member_inventory.entity_id,
                        )
                    )
            else:
                continue

    def refill_ammunition(
        self,
        squad_member_inventory: EntityInventory,
        standard_inventory: list[BreedItemInfo],
        weapons_in_inventory: list[WeaponInfo],
    ) -> None:
        """Refill ammunition for weapons in inventory.

        Weapons that belong to the unit's standard template are topped up to
        their template amounts. Weapons outside the template (picked up or
        swapped during the campaign) are refilled from the precomputed soldier
        pickup defaults; if no unambiguous default exists, the weapon is
        skipped and logged instead of guessing.

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
            standard_inventory (list[BreedItemInfo]): Standard inventory items
            weapons_in_inventory (list[WeaponInfo]): Weapons currently in inventory
        """
        template_weapons = set(
            self.knowledge_base.find_weapons_in_breed_inventory_entries(
                standard_inventory
            )
        )

        for weapon_info in weapons_in_inventory:
            weapon_name = weapon_info.weapon_name
            weapon_type = weapon_info.weapon_type.split("\\")[-1]

            if weapon_name not in template_weapons:
                pickup_ammo = self._resolve_pickup_ammo(
                    weapon_info, UNIT_CLASS_SOLDIER
                )
                if pickup_ammo is None:
                    self.logger.log(
                        f"No pickup ammo default for {weapon_name} in "
                        f"{squad_member_inventory.entity_id} inventory; skipping."
                    )
                    continue
                self._refill_ammo_item(squad_member_inventory, pickup_ammo)
                continue

            # Process each ammo item in the unit's own template inventory
            for i, item in enumerate(standard_inventory):
                if not "ammo" in item.game_item_name:
                    continue

                ammo_type = self._determine_ammo_type(
                    item, weapon_name, weapon_type, standard_inventory, i
                )
                if not ammo_type:
                    continue

                self._refill_ammo_item(squad_member_inventory, item)

    def refill_vehicle_ammunition(
        self,
        squad_member_inventory: EntityInventory,
        standard_inventory: list[BreedItemInfo],
    ) -> None:
        """Refill vehicle ammunition from the current vehicle inventory.

        The current vehicle inventory is always the primary source of truth. A
        fallback to other vehicles/breeds is used only when the current vehicle
        does not define the weapon at all; it is never used to override a precise
        weapon-family match already present on this vehicle.

        Args:
            squad_member_inventory (EntityInventory): The vehicle's inventory
            standard_inventory (list[BreedItemInfo]): Standard inventory items
        """
        # Find weapons in inventory
        weapons_in_inventory = squad_member_inventory.find_gun_entries_in_inventory()
        weapons_in_vehicle_inventory = [
            weapon_info.weapon_name for weapon_info in weapons_in_inventory
        ]
        weapons_in_standard_inventory = (
            self.knowledge_base.find_weapons_in_breed_inventory_entries(
                breed_inventory_entries=standard_inventory
            )
        )

        # Add missing weapons if needed
        if weapons_in_standard_inventory and not weapons_in_vehicle_inventory:
            self.refill_weapons(
                squad_member_inventory=squad_member_inventory,
                standard_inventory=standard_inventory,
            )
            weapons_in_inventory = (
                squad_member_inventory.find_gun_entries_in_inventory()
            )
            weapons_in_vehicle_inventory = [
                weapon_info.weapon_name for weapon_info in weapons_in_inventory
            ]
            if weapons_in_vehicle_inventory:
                self.logger.log(
                    f"Added missing weapons to {squad_member_inventory.entity_id} inventory"
                )

        # Process bullets and hidden weapons in standard inventory
        for item in standard_inventory:
            item_name = item.game_item_name

            pattern = r"(\d+)mm_"
            matches = re.findall(pattern, item_name)
            if matches and ".ammo" in item_name:
                self._refill_vehicle_standard_ammo(
                    squad_member_inventory=squad_member_inventory, item=item
                )
            elif any(item_elem in item_name for item_elem in ["bullet", "mortar"]):
                self._refill_vehicle_standard_ammo(
                    squad_member_inventory=squad_member_inventory, item=item
                )
            elif item_name in self.knowledge_base.weapons_list and not item.is_visible:
                weapon_info = self.knowledge_base.find_weapon_in_weapons_info_list(
                    item_name
                )
                if weapon_info is None:
                    continue

                weapons_in_inventory.insert(
                    0,
                    WeaponInfo(
                        weapon_name=item_name,
                        weapon_type=weapon_info.weapon_type,
                    ),
                )
                weapons_in_vehicle_inventory.insert(0, item_name)

        # Process ammunition for each machinegun weapon present in inventory.
        # Template weapons are topped up from the vehicle's own template
        # inventory; weapons outside the template (added during the campaign)
        # are refilled from the precomputed vehicle pickup defaults. Weapons
        # that cannot be resolved unambiguously are skipped and logged.
        for weapon_info in weapons_in_inventory:
            weapon_name = weapon_info.weapon_name
            weapon_type = weapon_info.weapon_type.split("\\")[-1]

            if weapon_type != "mgun":
                continue

            refilled_ammo = False
            if weapon_name in weapons_in_standard_inventory:
                for i, item in enumerate(standard_inventory):
                    if (
                        "ammo" not in item.game_item_name
                        or "bullet" in item.game_item_name
                    ):
                        continue

                    ammo_type = self._determine_vehicle_ammo_type(
                        item, weapon_name, weapon_type, standard_inventory, i
                    )

                    if ammo_type:
                        refilled_ammo = self._refill_vehicle_standard_ammo(
                            squad_member_inventory, item, item.amount
                        )
                        break
            else:
                pickup_ammo = self._resolve_pickup_ammo(
                    weapon_info, UNIT_CLASS_VEHICLE
                )
                if pickup_ammo is None:
                    self.logger.log(
                        f"No pickup ammo default for {weapon_name} in "
                        f"{squad_member_inventory.entity_id} inventory; skipping."
                    )
                    continue
                refilled_ammo = self._refill_vehicle_standard_ammo(
                    squad_member_inventory, pickup_ammo, pickup_ammo.amount
                )

            if refilled_ammo:
                self.logger.log(
                    f"Refilled ammunition for {weapon_name} in {squad_member_inventory.entity_id} inventory"
                )

    def _resolve_pickup_ammo(
        self, weapon_info: WeaponInfo, unit_class: str
    ) -> BreedItemInfo | None:
        """Resolve default ammo for a weapon outside the unit's template.

        Candidates come from the precomputed per-class pickup defaults table
        and are filtered by the strict weapon-family matcher. A single
        unambiguous candidate is returned; ties and unknown weapons resolve
        to None so the caller can skip instead of guessing.

        Args:
            weapon_info (WeaponInfo): Weapon to resolve ammo for
            unit_class (str): "soldier" or "vehicle" defaults table to use

        Returns:
            BreedItemInfo | None: Ammo item with default amount, or None
        """
        defaults = getattr(self.knowledge_base, "pickup_ammo_defaults", {}).get(
            unit_class, {}
        )
        if not defaults:
            return None

        candidates: list[BreedItemInfo] = []
        for ammo_name, amount in defaults.items():
            candidate = BreedItemInfo(game_item_name=ammo_name, amount=amount)
            resolved = self._determine_vehicle_ammo_type(
                candidate,
                weapon_info.weapon_name,
                weapon_info.weapon_type,
                [],
                0,
            )
            if resolved:
                candidates.append(candidate)

        if len(candidates) == 1:
            return candidates[0]
        if not candidates:
            return None

        normalized_weapon = re.sub(
            r"[^a-z0-9]+", "_", weapon_info.weapon_name.lower()
        ).strip("_")

        # Multiple family-matched candidates: prefer the base variant (fewest
        # tokens, e.g. "hmgun_usa.ammo" over "hmgun_usa.api.ammo"), then the
        # highest name similarity. Only a true tie is skipped as ambiguous.
        scored = []
        for item in candidates:
            normalized_ammo = re.sub(
                r"[^a-z0-9]+", "_", item.game_item_name.lower()
            ).strip("_")
            token_count = len([token for token in normalized_ammo.split("_") if token])
            similarity = SequenceMatcher(None, normalized_weapon, normalized_ammo).ratio()
            scored.append((token_count, -similarity, item))

        scored.sort(key=lambda entry: (entry[0], entry[1]))
        best_key = (scored[0][0], scored[0][1])
        best_matches = [
            item for token_count, neg_similarity, item in scored
            if (token_count, neg_similarity) == best_key
        ]
        if len(best_matches) == 1:
            return best_matches[0]

        self.logger.log(
            f"Ambiguous pickup ammo for {weapon_info.weapon_name}: "
            f"{[item.game_item_name for item in best_matches]}. Skipping."
        )
        return None

    def _refill_vehicle_standard_ammo(
        self,
        squad_member_inventory: EntityInventory,
        item: BreedItemInfo,
        target_amount: int | None = None,
    ) -> bool:
        """Refill vehicle standard ammunition to target amount.

        Args:
            squad_member_inventory (EntityInventory): The vehicle's inventory
            item (BreedItemInfo): Ammunition item to refill
            target_amount (int, optional): Target amount to refill to

        Returns:
            bool: True if ammunition was successfully refilled
        """
        item_name = item.game_item_name
        target_amount = target_amount or item.amount
        item_counts = squad_member_inventory.item_counts or {}
        current_amount = item_counts.get(item_name, 0)

        if current_amount >= target_amount:
            return False

        item_mass = self.knowledge_base.item_weights[item_name]
        item_refill_cost = round(item_mass * (target_amount - current_amount), 1)

        campaign_status_info = self.knowledge_base.campaign_status_info
        if campaign_status_info is None:
            self.logger.log("Campaign status information is not initialized.")
            return False

        if campaign_status_info.ap - item_refill_cost < 0:
            self.logger.log(
                f"Not enough AP to refill {item_name} in {squad_member_inventory.entity_id} inventory."
            )
            return False

        # Fill existing stacks first
        filled_amount = 0
        difference = 1  # Initialize to enter loop
        while difference > 0:
            difference = squad_member_inventory.fill_item_in_inventory(
                item_name,
                current_inventory_amount=current_amount,
                max_amount=target_amount,
            )
            filled_amount += difference
            current_amount += filled_amount

        # Add new stack if needed
        remaining_amount = target_amount - current_amount
        if remaining_amount > 0:
            squad_member_inventory.add_item_to_inventory(
                item_name, amount=remaining_amount
            )
            self.logger.log(
                f"Added {remaining_amount} of {item_name} to inventory of {squad_member_inventory.entity_id}."
            )

        total_added = filled_amount + (remaining_amount if remaining_amount > 0 else 0)
        if total_added > 0:
            self.logger.log(
                f"Total {total_added} of {item_name} for {item_refill_cost} AP added to {squad_member_inventory.entity_id}."
            )

        squad_member_inventory.count_items_in_inventory()

        campaign_status_info.ap -= item_refill_cost
        return True

    def _determine_ammo_type(
        self,
        item: BreedItemInfo,
        weapon_name: str,
        weapon_type: str,
        inventory: list,
        index: int,
    ) -> str:
        """Determine ammunition type for a weapon.

        This is the generic soldier-weapon logic and intentionally keeps the broader
        fallback behavior so the human squad refill flow remains unchanged.

        Args:
            item (BreedItemInfo): Item to check
            weapon_name (str): Name of the weapon
            weapon_type (str): Type of the weapon
            inventory (list): Inventory items list
            index (int): Index in inventory

        Returns:
            str: Ammunition type or empty string if not found
        """
        if BROWNING_M2_WEAPON in weapon_name:
            if HMGUN_USA_AMMO in item.game_item_name:
                return item.game_item_name
            return ""
        if weapon_type in item.game_item_name:
            return item.game_item_name
        if (
            SequenceMatcher(None, weapon_name, item.game_item_name).ratio()
            >= SIMILARITY_THRESHOLD
        ):
            return item.game_item_name
        if index > 0 and inventory[index - 1].game_item_name == weapon_name:
            return item.game_item_name
        return ""

    def _determine_vehicle_ammo_type(
        self,
        item: BreedItemInfo,
        weapon_name: str,
        weapon_type: str,
        inventory: list,
        index: int,
    ) -> str:
        """Determine ammunition type for vehicle-mounted weapons.

        Vehicle ammo matching must be precise because some American vehicles carry
        both standard Browning MG ammo and heavy Browning HMG ammo in the same
        inventory. This helper rejects mismatched families instead of selecting the
        first generic machinegun match.

        Args:
            item (BreedItemInfo): Item to check
            weapon_name (str): Name of the weapon
            weapon_type (str): Type of the weapon
            inventory (list): Inventory items list
            index (int): Index in inventory

        Returns:
            str: Ammunition type or empty string if not found
        """
        if "ammo" not in item.game_item_name or "bullet" in item.game_item_name:
            return ""

        normalized_weapon_name = re.sub(
            r"[^a-z0-9]+", "_", weapon_name.lower()
        ).strip("_")
        normalized_item_name = re.sub(
            r"[^a-z0-9]+", "_", item.game_item_name.lower()
        ).strip("_")

        item_tokens = set(token for token in normalized_item_name.split("_") if token)
        weapon_tokens = set(token for token in normalized_weapon_name.split("_") if token)

        item_is_heavy_mg_ammo = "hmgun" in item_tokens
        item_is_standard_mg_ammo = "mgun" in item_tokens

        weapon_is_heavy_mg = (
            "browning_m2" in normalized_weapon_name
            or "m2hb" in normalized_weapon_name
            or "m2_hb" in normalized_weapon_name
        )
        weapon_is_standard_mg = (
            "browning_m19a4" in normalized_weapon_name
            or "m1917" in normalized_weapon_name
            or "browning_m1917" in normalized_weapon_name
            or (
                "mgun" in weapon_tokens
                and "hmgun" not in weapon_tokens
                and "m2" not in weapon_tokens
            )
        )

        if weapon_is_heavy_mg and item_is_heavy_mg_ammo and not item_is_standard_mg_ammo:
            return item.game_item_name
        if weapon_is_standard_mg and item_is_standard_mg_ammo and not item_is_heavy_mg_ammo:
            return item.game_item_name

        if (
            SequenceMatcher(None, weapon_name, item.game_item_name).ratio()
            >= SIMILARITY_THRESHOLD
        ):
            return item.game_item_name
        if index > 0 and inventory[index - 1].game_item_name == weapon_name:
            return item.game_item_name
        return ""

    def _refill_ammo_item(
        self,
        squad_member_inventory: EntityInventory,
        item: BreedItemInfo,
    ) -> None:
        """Refill specific ammunition item to target amount.

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
            item (BreedItemInfo): Ammunition item to refill
        """
        item_name = item.game_item_name
        item_counts = squad_member_inventory.item_counts or {}
        current_amount = item_counts.get(item_name, 0)

        target_amount = item.amount

        if current_amount >= target_amount:
            return

        item_mass = self.knowledge_base.item_weights[item_name]
        item_refill_cost = round(item_mass * (target_amount - current_amount), 1)
        campaign_status_info = self.knowledge_base.campaign_status_info
        if campaign_status_info is None:
            self.logger.log("Campaign status information is not initialized.")
            return

        if campaign_status_info.ap - item_refill_cost < 0:
            self.logger.log(
                f"Not enough AP to refill {item_name} in {squad_member_inventory.entity_id} inventory."
            )
            return

        item_block_size = int(self.knowledge_base.item_block_sizes.get(item_name, "1"))

        # Fill existing stacks first
        filled_amount = 0
        while True:
            difference = squad_member_inventory.fill_item_in_inventory(
                item_name,
                current_inventory_amount=current_amount,
                max_amount=item_block_size,
            )
            if difference == 0:
                break
            filled_amount += difference
            current_amount += filled_amount

        # Add new stacks if needed
        remaining_amount = target_amount - current_amount
        if remaining_amount <= 0:
            self.logger.log(
                f"Total {filled_amount} of {item_name} added to {squad_member_inventory.entity_id} for {item_refill_cost} AP."
            )
            return

        full_stacks = remaining_amount // item_block_size
        remainder = remaining_amount % item_block_size

        for _ in range(full_stacks):
            if squad_member_inventory.add_item_to_inventory(
                item_name, amount=item_block_size
            ):
                self.logger.log(
                    f"Added {item_block_size} of {item_name} to inventory of {squad_member_inventory.entity_id}."
                )

        if remainder > 0:
            if squad_member_inventory.add_item_to_inventory(
                item_name, amount=remainder
            ):
                self.logger.log(
                    f"Added {remainder} of {item_name} to inventory of {squad_member_inventory.entity_id}."
                )

        campaign_status_info.ap -= item_refill_cost

        self.logger.log(
            f"Total {filled_amount + remaining_amount} of {item_name} for {item_refill_cost} AP added to {squad_member_inventory.entity_id}."
        )

    def refill_supplies_resources(
        self, squad_member_inventory: EntityInventory
    ) -> None:
        """Refill human squad member's supplies and resources.

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
        """
        # Here resources are shown as a number from 0 to 10
        # They have to be multiplied by 10 to get the actual amount
        missing_resources = (
            MAX_RESOURCES - squad_member_inventory.resources
        ) * RESOURCE_MULTIPLIER
        missing_resources_cost = round(missing_resources * 0.25, 1)
        campaign_status_info = self.knowledge_base.campaign_status_info
        if campaign_status_info is None:
            self.logger.log("Campaign status information is not initialized.")
            return

        if campaign_status_info.ap - missing_resources_cost < 0:
            self.logger.log(
                LOG_NOT_ENOUGH_AP_ITEM.format(
                    item_type="supplies/resources",
                    entity_id=squad_member_inventory.entity_id,
                )
            )
            return

        squad_member_inventory.resources = MAX_RESOURCES
        campaign_status_info.ap -= missing_resources_cost

        self.logger.log(
            LOG_RESOURCES_ADDED.format(
                amount=missing_resources,
                entity_id=squad_member_inventory.entity_id,
                cost=missing_resources_cost,
            )
        )

    def refill_supplies(self, squad_member_inventory: EntityInventory) -> None:
        """Refill vehicle supplies to maximum.

        Args:
            squad_member_inventory (EntityInventory): The vehicle's inventory
        """
        # Here supplies are missing supplies
        missing_supplies = squad_member_inventory.supplies
        missing_supplies_cost = round(missing_supplies * 0.15, 1)
        campaign_status_info = self.knowledge_base.campaign_status_info
        if campaign_status_info is None:
            self.logger.log("Campaign status information is not initialized.")
            return

        if campaign_status_info.ap - missing_supplies_cost < 0:
            self.logger.log(
                f"Not enough AP to refill supplies in {squad_member_inventory.entity_id} inventory."
            )
            return

        # After the refill there are 0 missing supplies
        squad_member_inventory.supplies = 0
        campaign_status_info.ap -= missing_supplies_cost

        self.logger.log(
            f"Total {missing_supplies} supplies added to {squad_member_inventory.entity_id} for {missing_supplies_cost} AP."
        )

    def refill_fuel(self, squad_member_inventory: EntityInventory) -> None:
        """Refill vehicle fuel to maximum capacity.

        Args:
            squad_member_inventory (EntityInventory): The vehicle's inventory
        """
        missing_fuel = round(
            self.knowledge_base.vehicles_fuel_properties[
                squad_member_inventory.entity_breed
            ]
            - squad_member_inventory.fuel,
            4,
        )
        if missing_fuel <= 0:
            return
        missing_fuel_cost = round(missing_fuel * 0.25, 1)
        campaign_status_info = self.knowledge_base.campaign_status_info
        if campaign_status_info is None:
            self.logger.log("Campaign status information is not initialized.")
            return

        if campaign_status_info.ap - missing_fuel_cost < 0:
            self.logger.log(
                f"Not enough AP to refill fuel in {squad_member_inventory.entity_id} inventory."
            )
            return

        squad_member_inventory.fuel = self.knowledge_base.vehicles_fuel_properties[
            squad_member_inventory.entity_breed
        ]
        campaign_status_info.ap -= missing_fuel_cost

        self.logger.log(
            f"Total {missing_fuel} fuel added to {squad_member_inventory.entity_id} for {missing_fuel_cost} AP."
        )

    def refill_missing_squad_members(self, squad_id: int) -> None:
        """Refill missing squad members with substitutes.

        Args:
            squad_id (int): The squad identifier
        """

        squad_name = self.squads[squad_id].squad_name.strip('"')
        squad_inventory = self.squads_inventories[squad_id]
        member_counts = {}
        for (
            _,
            squad_member_inventory,
        ) in squad_inventory.inventories.items():
            member_name = squad_member_inventory.entity_breed
            if member_name not in member_counts:
                member_counts[member_name] = 0
            member_counts[member_name] += 1

        campaign_status_info = self.knowledge_base.campaign_status_info
        if campaign_status_info is None:
            self.logger.log("Campaign status information is not initialized.")
            return

        conflict_side = campaign_status_info.army

        standard_squad_composition = self.knowledge_base.squad_compositions[squad_name]
        standard_squad_members = standard_squad_composition.members

        standard_squad_members_substituted = {}
        for squad_member, amount in standard_squad_members.items():
            if (
                conflict_side not in squad_member
                and squad_member in UNITS_SUBSTITUTIONS
            ):
                breed = UNITS_SUBSTITUTIONS[squad_member]
            else:
                breed = _substitute_army_key_in_breed(squad_member, conflict_side)

            if breed not in standard_squad_members_substituted:
                standard_squad_members_substituted[breed] = 0
            standard_squad_members_substituted[breed] += amount

        standard_squad_members = standard_squad_members_substituted

        number_of_current_squad_members = sum(member_counts.values())
        number_of_standard_squad_members = sum(standard_squad_members.values())
        if number_of_current_squad_members >= number_of_standard_squad_members:
            self.logger.log(
                "Squad has maximum number of members... Cannot add more members!"
            )
            return
        if squad_id in self.new_units_resupplied_squads:
            self.logger.log("Squad has already been resupplied with new members!")
            return

        new_unit_entries = []
        total_cost = 0.0
        for standard_member, standard_member_count in standard_squad_members.items():
            current_member_count = member_counts.get(standard_member, 0)

            if current_member_count < standard_member_count:
                for _ in range(standard_member_count - current_member_count):
                    if (
                        number_of_current_squad_members + len(new_unit_entries)
                        >= number_of_standard_squad_members
                    ):
                        break
                    breed = standard_member
                    cost = 0.0
                    if f"mp/" in standard_member:
                        if standard_member in self.knowledge_base.infantry_costs:
                            cost = self.knowledge_base.infantry_costs[standard_member]
                        else:
                            self.logger.log(
                                f"Could not find {standard_member} in infantry costs!"
                            )
                            continue
                    else:
                        if standard_member in self.knowledge_base.vehicles_costs:
                            cost = self.knowledge_base.vehicles_costs[standard_member]
                        else:
                            self.logger.log(
                                f"Could not find {standard_member} in vehicles costs!"
                            )
                            continue

                    campaign_status_info = self.knowledge_base.campaign_status_info
                    if campaign_status_info is None:
                        self.logger.log("Campaign status information is not initialized.")
                        return

                    if campaign_status_info.mp - cost < 0:
                        self.logger.log(
                            LOG_NOT_ENOUGH_MP_UNIT.format(
                                breed=breed, squad_name=squad_name
                            )
                        )
                        continue
                    unit_entry = self.create_new_squad_member(
                        squad_id=squad_id, breed=breed
                    )
                    new_unit_entries.append(unit_entry)
                    campaign_status_info.mp -= cost
                    total_cost += cost
                    if squad_id not in self.new_units_resupplied_squads:
                        self.new_units_resupplied_squads.append(squad_id)

        self.new_unit_entries.extend(new_unit_entries)

        for unit_entry in new_unit_entries:
            self.logger.log(
                LOG_NEW_UNIT_ENTRY.format(squad_name=squad_name, unit_entry=unit_entry)
            )

        self.logger.log(
            LOG_NEW_SQUAD_MEMBERS.format(
                count=len(new_unit_entries), squad_name=squad_name, cost=total_cost
            )
        )

    def create_new_squad_member(self, squad_id: int, breed: str) -> str:
        """Create a new squad member with unique ID.

        Args:
            squad_id (int): The squad identifier
            breed (str): The breed type for the new member

        Returns:
            str: Unit entry string for the new squad member
        """
        while new_member_id := self.generate_random_hex():
            if new_member_id not in self.squad_members_ids:
                break

        squad_entry = self.squads_entries[squad_id]
        new_squad_entry = squad_entry.replace(DECEASED_MEMBER_ID, new_member_id, 1)
        self.squads_entries[squad_id] = new_squad_entry

        if MP_PREFIX in breed:
            unit_type = UNIT_TYPE_HUMAN
        else:
            unit_type = UNIT_TYPE_ENTITY

        unit_entry = f'{{{unit_type} "{breed}" {new_member_id}}}\n'

        self.squad_members_ids.append(new_member_id)

        return unit_entry

    def get_all_squad_members_ids(self) -> list[str]:
        """Get all squad member IDs from inventories.

        Returns:
            list[str]: List of all squad member identifiers
        """
        all_squad_members_ids = []
        for squad_inventory in self.squads_inventories:
            all_squad_members_ids.extend(squad_inventory.inventories.keys())
        return all_squad_members_ids

    def generate_random_hex(self) -> str:
        """Generate a random hexadecimal identifier.

        Returns:
            str: Random hex string in format 0x8000-0xFFFF
        """
        # Generate a random integer in the range
        random_int = random.randint(HEX_RANGE_MIN, HEX_RANGE_MAX)

        # Convert to hex string with "0x" prefix
        hex_string = f"{HEX_PREFIX}{random_int:x}"

        return hex_string

    def save_changes(self) -> None:
        """Save all changes to campaign files and inventories."""
        self.data_manager.create_campaign_file_backup()
        self.data_manager.create_campaign_status_file_backup()
        for squad_inventory in self.squads_inventories:
            for _, inventory in squad_inventory.inventories.items():
                if inventory.inventory_entries:
                    self.data_manager.save_squad_member_inventory(inventory)

        if self.new_unit_entries:
            self.data_manager.save_new_squad_members(
                new_unit_entries=self.new_unit_entries,
                squads_entries=self.squads_entries,
            )
            self.new_unit_entries.clear()

        self.data_manager.save_campaign_status_info()

        self.data_manager.save_campaign_file()
