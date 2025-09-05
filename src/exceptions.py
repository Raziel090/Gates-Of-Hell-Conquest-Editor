"""Custom exceptions for inventory management operations."""


class InventoryError(Exception):
    """Base exception for inventory-related errors."""

    pass


class ItemFitError(InventoryError):
    """Raised when an item doesn't fit in the inventory."""

    pass
