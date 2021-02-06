"""Inventory Transaction Model"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.timezone import now

from .item import Item
from .managers.transaction import ConsumptionHistoryManager, ExpiryManager
from .validators.transaction import validate_transaction_quantity

User = get_user_model()


class Transaction(models.Model):
  """Inventory Transaction Model"""
  datetime = models.DateTimeField(default=now)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  quantity = models.IntegerField(validators=[validate_transaction_quantity])

  consumption = ConsumptionHistoryManager()
  expiration = ExpiryManager()
  objects = models.Manager()

  class Meta:
    indexes = [
        models.Index(fields=['datetime']),
    ]

  @property
  def operation(self):
    """Returns a string indicating if the quantity is consumption or purchase.

    :returns: A string describing the transaaction
    :rtype: str
    """
    if isinstance(self.quantity, int):
      if self.quantity > 0:
        return "Purchase"
      if self.quantity < 0:
        return "Consumption"
    return None

  def __str__(self):
    operation_type = self.operation
    if operation_type:
      return "%s: %s units of %s" % (
          self.operation,
          self.quantity,
          self.item.name,
      )
    return "Invalid Transaction"

  def clean(self):
    if (self.item.quantity + self.quantity) < 0:
      raise ValidationError([{
          'quantity': "This field may not reduce inventory below 0."
      }])
    super().clean()

  def apply_transaction(self):
    """Updates the related item quantity, and it's expiry."""
    if self.id is None:
      self.item.quantity = self.item.quantity + self.quantity
      Transaction.expiration.update(self)

  # pylint: disable=W0222
  def save(self, *args, **kwargs):
    with transaction.atomic():
      self.full_clean()
      self.apply_transaction()
      super(Transaction, self).save(*args, **kwargs)
      self.item.save()
