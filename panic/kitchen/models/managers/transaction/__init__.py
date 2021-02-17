"""Root Transaction model manager."""

from .consumption import ConsumptionHistoryManager


class TransactionManager(ConsumptionHistoryManager):
  """Aggregate sub-managers into a root Transaction model manager."""
