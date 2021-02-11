"""Inventory Transaction Model"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils.timezone import now

from .item import Item
from .transaction_managers import ConsumptionHistoryManager, ExpiryManager

User = get_user_model()


def validate_quantity(value):
  if value == 0:
    raise ValidationError([{'quantity': "Must not be equal to 0"}])
  return value


class Transaction(models.Model):
  """Inventory Transaction Model"""
  datetime = models.DateTimeField(default=now)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  quantity = models.IntegerField(validators=[validate_quantity])
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  consumption = ConsumptionHistoryManager()
  expiration = ExpiryManager()
  objects = models.Manager()

  class Meta:
    indexes = [
        models.Index(fields=['datetime']),
    ]

  @property
  def operation(self):
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

  def update_related_item_quantity(self):
    self.item.quantity = self.item.quantity + self.quantity

  def clean(self):
    if (self.item.quantity + self.quantity) < 0:
      raise ValidationError([{
          'quantity': "This field may not reduce inventory below 0."
      }])
    super().clean()

  # pylint: disable=W0222
  def save(self, *args, **kwargs):
    with transaction.atomic():
      self.full_clean()
      super(Transaction, self).save(*args, **kwargs)
      self.update_related_item_quantity()
      Transaction.expiration.update(self)
      self.item.save()
