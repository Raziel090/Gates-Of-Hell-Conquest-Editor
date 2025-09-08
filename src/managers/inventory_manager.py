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
}


# Constants for common strings
# Unit types
UNIT_TYPE_HUMAN = "Human"
UNIT_TYPE_ENTITY = "Entity"
PROPERTY_HUMAN = "human"

# Weapon/ammo related strings
BROWNING_M2_WEAPON = "browning_m2"
HMGUN_USA_AMMO = "hmgun_usa"
AMMO_KEYWORD = "ammo"
BULLET_KEYWORD = "bullet"
MP_PREFIX = "mp/"
UNDERSCORE_SEPARATOR = "_"

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

    def prepare_squads_and_inventories(self) -> None:
        """Prepare squad data and collect all member IDs."""
        super().prepare_squads_and_inventories(keep_deceased_members=False)
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

            item_refill_cost = self.knowledge_base.item_weights[item_name]
            if self.knowledge_base.campaign_status_info.ap - item_refill_cost < 0:
                self.logger.log(
                    f"Not enough AP to refill {item_name} in {squad_member_inventory.entity_id} inventory."
                )
                continue

            item_amount = 1
            added_item = squad_member_inventory.add_item_to_inventory(
                item_name, amount=item_amount
            )
            if added_item:
                self.knowledge_base.campaign_status_info.ap -= item_refill_cost

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
            squad_member_inventory_amount = squad_member_inventory.item_counts.get(
                item_name, 0
            )

            if squad_member_inventory_amount < amount:
                item_amount = amount - squad_member_inventory_amount
                item_refill_cost = (
                    self.knowledge_base.item_weights[item_name] * item_amount
                )
                if self.knowledge_base.campaign_status_info.ap - item_refill_cost < 0:
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
                for _ in range(in_game_item_full_stacks):
                    added_item = squad_member_inventory.add_item_to_inventory(
                        item_name, amount=item_block_size
                    )
                if in_game_item_remainder > 0:
                    added_item = squad_member_inventory.add_item_to_inventory(
                        item_name, amount=in_game_item_remainder
                    )

                self.knowledge_base.campaign_status_info.ap -= item_refill_cost

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

        Args:
            squad_member_inventory (EntityInventory): The squad member's inventory
            standard_inventory (list[BreedItemInfo]): Standard inventory items
            weapons_in_inventory (list[WeaponInfo]): Weapons currently in inventory
        """
        for weapon_info in weapons_in_inventory:
            weapon_name = weapon_info.weapon_name
            weapon_type = weapon_info.weapon_type.split("\\")[-1]

            # Get matching breeds or similar items
            matching_breeds = self.knowledge_base.search_for_breed_with_weapon(
                weapon_name
            )
            if not matching_breeds:
                matching_breeds = self.search_for_similar_item(weapon_name)
                if not matching_breeds:
                    self.logger.log(
                        f"No breeds with {weapon_name} found in knowledge base!"
                    )
                    continue

            # Select appropriate inventory based on breed
            breed_standard_inventory = (
                standard_inventory
                if squad_member_inventory.entity_breed in matching_breeds
                else self.knowledge_base.breeds_inventories[
                    random.choice(matching_breeds)
                ]
            )

            # Process each ammo item in inventory
            for i, item in enumerate(breed_standard_inventory):
                if not "ammo" in item.game_item_name:
                    continue

                ammo_type = self._determine_ammo_type(
                    item, weapon_name, weapon_type, breed_standard_inventory, i
                )
                if not ammo_type:
                    continue

                self._refill_ammo_item(squad_member_inventory, item)

    def refill_vehicle_ammunition(
        self,
        squad_member_inventory: EntityInventory,
        standard_inventory: list[BreedItemInfo],
    ) -> None:
        """Refill vehicle ammunition from standard inventory.

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
                weapons_in_inventory.insert(
                    0,
                    WeaponInfo(
                        weapon_name=item_name,
                        weapon_type=weapon_info.weapon_type,
                    ),
                )
                weapons_in_vehicle_inventory.insert(0, item_name)

        # Process ammunition for each weapon
        ammo_counts = self._find_ammo_counts_in_vehicle_inventory_entries(
            standard_inventory
        )
        max_ammo_amount = self._find_max_ammo_amount_in_vehicle_inventory_entries(
            standard_inventory
        )

        # Only process weapons that are supposed to be in this vehicle type
        relevant_weapons = weapons_in_inventory[: len(weapons_in_standard_inventory)]

        for weapon_info in relevant_weapons:
            weapon_name = weapon_info.weapon_name
            weapon_type = weapon_info.weapon_type.split("\\")[-1]

            if weapon_type != "mgun":
                continue

            # Find appropriate inventory to use as reference
            vehicle_standard_inventory = None
            matching_vehicles = self.knowledge_base.search_for_vehicle_with_weapon(
                weapon_name
            )

            if matching_vehicles:
                chosen_vehicle = random.choice(matching_vehicles)
                vehicle_standard_inventory = self.knowledge_base.vehicle_inventories[
                    chosen_vehicle
                ]
            else:
                matching_breeds = self.search_for_similar_item(weapon_name)
                if matching_breeds:
                    chosen_breed = random.choice(matching_breeds)
                    vehicle_standard_inventory = self.knowledge_base.breeds_inventories[
                        chosen_breed
                    ]
                else:
                    self.logger.log(
                        f"No vehicles and breeds with {weapon_name} found in knowledge base!"
                    )
                    continue

            # Find and add appropriate ammo for this weapon
            refilled_ammo = False
            for i, item in enumerate(vehicle_standard_inventory):
                if "ammo" not in item.game_item_name or "bullet" in item.game_item_name:
                    continue

                ammo_type = self._determine_ammo_type(
                    item, weapon_name, weapon_type, vehicle_standard_inventory, i
                )

                if ammo_type:
                    ammo_amount = ammo_counts.get(
                        ammo_type,
                        max_ammo_amount // len(weapons_in_standard_inventory) or 1,
                    )
                    refilled_ammo = self._refill_vehicle_standard_ammo(
                        squad_member_inventory, item, ammo_amount
                    )
                    break
            if refilled_ammo:
                self.logger.log(
                    f"Refilled ammunition for {weapon_name} in {squad_member_inventory.entity_id} inventory"
                )

    def _find_ammo_counts_in_vehicle_inventory_entries(
        self, vehicle_inventory: list[BreedItemInfo]
    ) -> dict[str, int]:
        """Find ammunition counts in vehicle inventory entries.

        Args:
            vehicle_inventory (list[BreedItemInfo]): Vehicle inventory items

        Returns:
            dict[str, int]: Mapping of ammo names to amounts
        """
        return {
            item.game_item_name: item.amount
            for item in vehicle_inventory
            if AMMO_KEYWORD in item.game_item_name
            and BULLET_KEYWORD not in item.game_item_name
        }

    def _refill_vehicle_standard_ammo(
        self,
        squad_member_inventory: EntityInventory,
        item: BreedItemInfo,
        target_amount: int = None,
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
        current_amount = squad_member_inventory.item_counts.get(item_name, 0)

        if current_amount >= target_amount:
            return False

        item_mass = self.knowledge_base.item_weights[item_name]
        item_refill_cost = round(item_mass * (target_amount - current_amount), 1)

        if self.knowledge_base.campaign_status_info.ap - item_refill_cost < 0:
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

        self.knowledge_base.campaign_status_info.ap -= item_refill_cost
        return True

    def _find_max_ammo_amount_in_vehicle_inventory_entries(
        self, vehicle_inventory: list[BreedItemInfo]
    ) -> int:
        """Find maximum ammunition amount in vehicle inventory.

        Args:
            vehicle_inventory (list[BreedItemInfo]): Vehicle inventory items

        Returns:
            int: Maximum ammunition amount found
        """
        ammo_amounts = [
            item.amount
            for item in vehicle_inventory
            if AMMO_KEYWORD in item.game_item_name
            and BULLET_KEYWORD not in item.game_item_name
        ]
        return max(ammo_amounts, default=0)

    def _determine_ammo_type(
        self,
        item: BreedItemInfo,
        weapon_name: str,
        weapon_type: str,
        inventory: list,
        index: int,
    ) -> str:
        """Determine ammunition type for a weapon.

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
        current_amount = squad_member_inventory.item_counts.get(item_name, 0)

        target_amount = item.amount

        if current_amount >= target_amount:
            return

        item_mass = self.knowledge_base.item_weights[item_name]
        item_refill_cost = round(item_mass * (target_amount - current_amount), 1)
        if self.knowledge_base.campaign_status_info.ap - item_refill_cost < 0:
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

        self.knowledge_base.campaign_status_info.ap -= item_refill_cost

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
        if self.knowledge_base.campaign_status_info.ap - missing_resources_cost < 0:
            self.logger.log(
                LOG_NOT_ENOUGH_AP_ITEM.format(
                    item_type="supplies/resources",
                    entity_id=squad_member_inventory.entity_id,
                )
            )
            return

        squad_member_inventory.resources = MAX_RESOURCES
        self.knowledge_base.campaign_status_info.ap -= missing_resources_cost

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
        if self.knowledge_base.campaign_status_info.ap - missing_supplies_cost < 0:
            self.logger.log(
                f"Not enough AP to refill supplies in {squad_member_inventory.entity_id} inventory."
            )
            return

        # After the refill there are 0 missing supplies
        squad_member_inventory.supplies = 0
        self.knowledge_base.campaign_status_info.ap -= missing_supplies_cost

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
        if self.knowledge_base.campaign_status_info.ap - missing_fuel_cost < 0:
            self.logger.log(
                f"Not enough AP to refill fuel in {squad_member_inventory.entity_id} inventory."
            )
            return

        squad_member_inventory.fuel = self.knowledge_base.vehicles_fuel_properties[
            squad_member_inventory.entity_breed
        ]
        self.knowledge_base.campaign_status_info.ap -= missing_fuel_cost

        self.logger.log(
            f"Total {missing_fuel} fuel added to {squad_member_inventory.entity_id} for {missing_fuel_cost} AP."
        )

    def refill_missing_squad_members(self, squad_id: int) -> None:
        """Refill missing squad members with substitutes.

        Args:
            squad_id (int): The squad identifier
        """

        def _substitute_army_key_in_breed(breed: str, army: str) -> str:
            if MP_PREFIX in breed:
                breed_split = breed.split("/")
                breed_split[1] = army
                return "/".join(breed_split)
            return breed

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

        conflict_side = self.knowledge_base.campaign_status_info.army

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

                    if self.knowledge_base.campaign_status_info.mp - cost < 0:
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
                    self.knowledge_base.campaign_status_info.mp -= cost
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

    def search_for_similar_item(self, item_name: str) -> list[str]:
        """Search for breeds that have similar item names.

        Args:
            item_name (str): The item name to search for

        Returns:
            list[str]: List of breed names with matching items
        """
        item_name = item_name.split(UNDERSCORE_SEPARATOR)[0]
        matching_breeds = self.knowledge_base.search_for_breed_with_item(item_name)
        return matching_breeds

    def save_changes(self) -> None:
        """Save all changes to campaign files and inventories."""
        self.data_manager.create_campaign_file_backup()
        self.data_manager.create_campaign_status_file_backup()
        for squad_inventory in self.squads_inventories:
            for _, inventory in squad_inventory.inventories.items():
                self.data_manager.save_squad_member_inventory(inventory)

        if self.new_unit_entries:
            self.data_manager.save_new_squad_members(
                new_unit_entries=self.new_unit_entries,
                squads_entries=self.squads_entries,
            )
            self.new_unit_entries.clear()

        self.data_manager.save_campaign_status_info()

        self.data_manager.save_campaign_file()
