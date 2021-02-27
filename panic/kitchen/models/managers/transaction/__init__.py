"""Root Transaction model manager."""

from .consumption import ConsumptionHistoryManager
from .maintenance import MaintenanceManager


class TransactionManager(
    ConsumptionHistoryManager,
    MaintenanceManager,
):
  """Aggregate sub-managers into a root Transaction model manager."""
