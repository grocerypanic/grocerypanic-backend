"""Root Transaction model manager."""

from .activity import ActivityManager
from .maintenance import MaintenanceManager


class TransactionManager(
    ActivityManager,
    MaintenanceManager,
):
  """Aggregate sub-managers into a root Transaction model manager."""
