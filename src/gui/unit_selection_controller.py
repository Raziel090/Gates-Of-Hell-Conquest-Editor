"""Controller helpers for unit-manager selection workflows."""

from __future__ import annotations

from typing import Sequence


class UnitSelectionController:
    """Coordinate squad and member selection for the unit manager tab."""

    def build_target_squad_names(self, squad_names: Sequence[str], base_squad_id: int) -> list[str]:
        """Return the target-squad list excluding the currently selected base squad."""
        return [name for index, name in enumerate(squad_names) if index != base_squad_id]
