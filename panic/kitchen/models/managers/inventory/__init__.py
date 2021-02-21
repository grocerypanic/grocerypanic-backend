"""Root Inventory model manager."""

from .adjustment import AdjustmentManager
from .expiration import ExpirationManager
from .quantity import QuantityManager


class InventoryManager(
    AdjustmentManager,
    ExpirationManager,
    QuantityManager,
):
  """Aggregate sub-managers into a root Inventory model manager."""
