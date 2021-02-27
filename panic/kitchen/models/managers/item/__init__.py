"""Root Item model manager."""

from .maintenance import MaintenanceManager


class ItemManager(
    MaintenanceManager,
):
  """Aggregate sub-managers into a root Item model manager."""
