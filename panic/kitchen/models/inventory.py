"""Inventory model."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from . import constants
from .managers.inventory import InventoryManager
from .mixins import FullCleanMixin, RelatedFieldEnforcementMixin

User = get_user_model()


class Inventory(
    FullCleanMixin,
    RelatedFieldEnforcementMixin,
    models.Model,
):
  """Inventory model."""

  item = models.ForeignKey('Item', on_delete=models.CASCADE)
  remaining = models.FloatField(
      validators=[
          MinValueValidator(constants.MINIMUM_QUANTITY),
          MaxValueValidator(constants.MAXIMUM_QUANTITY),
      ],
  )
  transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE)

  objects = InventoryManager()

  class Meta:
    verbose_name_plural = "Inventory"

  def __str__(self):
    return "%s units of %s, purchased at %s" % (
        self.remaining,
        self.item.name,
        self.transaction.datetime,
    )

  def clean(self):
    """Clean model."""
    super().clean()
    fields = ["transaction"]
    self.related_validator(fields, owner_field="item")
