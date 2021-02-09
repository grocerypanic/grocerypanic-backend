"""Inventory Transaction Model Managers"""

from django.db import models

from ...exceptions import ProcessingError


class InventoryTransactionManager(models.Manager):
  """Provides Methods to Modify Inventory Based on Incoming Transaction"""

  def process(self, transaction):
    if transaction.quantity > 0:
      self.credit(transaction)
    else:
      self.debit(transaction)

  def credit(self, transaction):
    super().get_queryset().create(
        transaction=transaction,
        item=transaction.item,
        remaining=transaction.quantity
    )

  def debit(self, transaction):
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
