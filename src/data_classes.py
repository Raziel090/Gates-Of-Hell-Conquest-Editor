"""Data classes for squad and inventory management."""

from __future__ import annotations

from dataclasses import dataclass, field

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
    inventories: dict[str, EntityInventory] = field(default_factory=dict)

    def add_inventory(self, squad_member_id: str, inventory: EntityInventory) -> None:
        """Attach a squad member inventory to this squad container."""
        self.inventories[squad_member_id] = inventory
