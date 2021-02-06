"""Inventory Model"""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .item import MAXIMUM_QUANTITY, MINIMUM_QUANTITY
from .managers.inventory import InventoryTransactionManager

User = get_user_model()


class Inventory(models.Model):
  """Inventory Model"""
  item = models.ForeignKey('Item', on_delete=models.CASCADE)
  remaining = models.FloatField(
      validators=[
          MinValueValidator(MINIMUM_QUANTITY),
          MaxValueValidator(MAXIMUM_QUANTITY),
      ],
  )
  transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE)

  objects = InventoryTransactionManager()

  class Meta:
    verbose_name_plural = "Inventory"

  def __str__(self):
    return "%s units of %s, purchased at %s" % (
        self.remaining,
        self.item.name,
        self.transaction.datetime,
    )

  # pylint: disable=W0222
  def save(self, *args, **kwargs):
    self.full_clean()
    super().save(*args, **kwargs)
