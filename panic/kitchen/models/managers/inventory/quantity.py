"""Inventory Quantity manager."""

from django.db import models
from django.db.models import Sum


class QuantityManager(models.Manager):
  """Retrieve Inventory quantity data for individual items."""

  def get_quantity(self, item):
    """Return the total inventory quantity of an item.

    :param item: A item instance to analyze
    :type item: :class:`kitchen.models.item.Item`

    :returns: A count of the total inventory, expressed as a float
    :rtype: float
    """
    total_quantity = 0
    queried_quantity = self.get_queryset().\
        filter(
          item=item
        ).\
        values(
          'remaining',
        ).\
        aggregate(
          quantity=Sum('remaining'),
        )['quantity']

    if queried_quantity:
      total_quantity = queried_quantity
    return total_quantity
