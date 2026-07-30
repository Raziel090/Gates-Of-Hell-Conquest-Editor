"""Controller helpers for unit move and exchange actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.managers.unit_manager import UnitManager


class UnitActionController:
    """Coordinate unit move and exchange operations for the GUI."""

    def resolve_effective_target_squad_id(
        self, target_squad_id: int, base_squad_id: int
    ) -> int:
        """Resolve the effective target squad index used during moves and exchanges."""
        if target_squad_id >= base_squad_id:
            return target_squad_id + 1
        return target_squad_id

    def move_unit(
        self,
        unit_manager: UnitManager,
        base_squad_id: int,
        base_unit_id: int,
        target_squad_id: int,
        target_unit_id: int | None,
        target_member_index: int | None,
    ) -> None:
        """Execute a move or exchange operation through the unit manager."""
        unit_manager.move_unit(
            base_squad_id,
            base_unit_id,
            target_squad_id,
            target_unit_id,
            target_member_index,
        )
