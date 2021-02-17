"""Root Inventory model manager."""

from .adjustment import AdjustmentManager
from .expiration import ExpirationManager


class InventoryManager(AdjustmentManager, ExpirationManager):
  """Aggregate sub-managers into a root Inventory model manager."""
