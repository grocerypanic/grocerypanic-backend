"""Inventory Maintenance manager."""

from django.core.paginator import Paginator
from django.db import models

from ....exceptions import ConfirmationRequired
from ...inventory import Inventory

ITEM_PAGE_SIZE = 250


class MaintenanceManager(models.Manager):
  """Perform maintenance tasks related to Item models."""

  def rebuild_quantities_from_inventory(self, confirm=False):
    """Recalculate all item quantities using Inventory data.

    :param confirm: A boolean indicating you REALLY want to do this
    :type confirm: bool

    :raises: :class:`panic.kitchen.exceptions.ConfirmationNeeded`
    """
    if not confirm:
      raise ConfirmationRequired("Are you sure you want to do this?")

    all_items = super().get_queryset().all().order_by('id')
    paginator = Paginator(all_items, ITEM_PAGE_SIZE)

    for page_number in paginator.page_range:
      page = paginator.page(page_number)

      for item in page.object_list:
        item.quantity = Inventory.objects.get_quantity(item)
        item.save()
