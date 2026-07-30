"""Small layout helpers for the Tkinter GUI panels."""


def resolve_target_squad_id(target_squad_id: int, base_squad_id: int) -> int:
    """Resolve the effective target-squad index for selection handling.

    The unit manager uses an offset when the target squad is selected after the
    base squad because the base squad selection is removed from the target list.
    """
    if target_squad_id >= base_squad_id:
        return target_squad_id + 1
    return target_squad_id
