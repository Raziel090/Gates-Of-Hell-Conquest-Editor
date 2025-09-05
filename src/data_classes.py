"""Data classes for squad and inventory management."""

from dataclasses import dataclass

from src.entity_inventory import EntityInventory


@dataclass
class SquadInfo:
    """Store squad identification and member information."""

    squad_id: int
    squad_name: str
    stage: str
    squad_members: list[str]


@dataclass
class SquadInventory:
    """Store squad inventory data with entity inventories."""

    squad_id: int
    inventories: dict[str, EntityInventory]
