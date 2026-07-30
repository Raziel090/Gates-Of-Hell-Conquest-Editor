"""Controller helpers for inventory-manager workflows."""

from __future__ import annotations

from typing import Mapping


class InventoryActionController:
    """Format inventory details and prepare resupply-related display text."""

    def format_inventory_details(self, item_counts: Mapping[str, int]) -> str:
        """Convert inventory item counts into readable multiline text."""
        return "\n".join(f"{key}: {value}" for key, value in item_counts.items())
