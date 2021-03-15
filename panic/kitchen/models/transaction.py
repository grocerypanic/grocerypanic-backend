"""Transaction model."""

from django.contrib.auth import get_user_model
from django.db import models, transaction
from django.utils.timezone import now

from . import constants
from .managers.transaction import TransactionManager
from .validators.transaction import (
    TransactionQuantityValidator,
    related_item_quantity_validator,
)

User = get_user_model()


class Transaction(models.Model):
  """Transaction model."""

  datetime = models.DateTimeField(default=now)
  item = models.ForeignKey('Item', on_delete=models.CASCADE)
  quantity = models.FloatField(
      validators=[TransactionQuantityValidator(constants.MAXIMUM_QUANTITY)]
  )

  objects = TransactionManager()

  class Meta:
    indexes = [
        models.Index(fields=['datetime']),
    ]

  @property
  def operation(self):
    """Return a string indicating if the quantity is consumption or purchase.

    :returns: A string describing the transaction
    :rtype: str
    """
    if isinstance(self.quantity, (float, int)):
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

  def apply_transaction_to_item(self, force=False):
    """Adjust fields on the related item with transaction data, and save.

    :param force: A boolean to force updates on existing transaction
    :type force: bool
    """
    if force or self.id is None:
      self.item.quantity += self.quantity
      self.item.save()

  def clean(self):
    """Validate the related item quantity changes we're about to make."""
    proposed_item_quantity = self.item.quantity + self.quantity
    related_item_quantity_validator(proposed_item_quantity)
    super().clean()

  # pylint: disable=signature-differs
  def save(self, *args, **kwargs):
    """Clean and save model."""
    with transaction.atomic():
      self.full_clean()
      self.apply_transaction_to_item()
      super().save(*args, **kwargs)
