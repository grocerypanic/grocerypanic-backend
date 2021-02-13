"""Inventory Transaction Model Managers"""

from django.db import models

from ...exceptions import ProcessingError


class InventoryTransactionManager(models.Manager):
  """Update the inventory based on transaction events."""

  def process(self, transaction):
    """Adjust a related item's inventory based on the transaction's quantity."""
    if transaction.quantity > 0:
      self.credit(transaction)
    else:
      self.debit(transaction)

  def credit(self, transaction):
    """Handle a positive inventory transaction."""
    super().get_queryset().create(
        transaction=transaction,
        item=transaction.item,
        remaining=transaction.quantity
    )

  def debit(self, transaction):
    """Handle a negative inventory transaction."""
    remaining = abs(transaction.quantity)
    inventory = super().get_queryset().\
        filter(item=transaction.item).\
        order_by("-transaction__datetime")

    for record in inventory:
      if record.remaining <= remaining:
        remaining = self.__debit_full_record(record, remaining)
      else:
        remaining = self.__debit_partial_record(record, remaining)
      if remaining < 1:
        return

    raise ProcessingError(
        detail=(
            f"Could not process transaction.id={transaction.id} to modify"
            f" item.id={transaction.item.id} quantity",
        ),
    )

  @staticmethod
  def __debit_full_record(record, remaining):
    remaining -= record.remaining
    record.delete()
    return remaining

  @staticmethod
  def __debit_partial_record(record, remaining):
    record_starting_value = record.remaining
    record.remaining -= remaining
    record.save()
    remaining -= (record_starting_value - record.remaining)
    return remaining
