"""Transaction Maintenance manager."""

from django.core.paginator import Paginator
from django.db import models

from ....exceptions import ConfirmationRequired
from ...inventory import Inventory

TRANSACTION_PAGE_SIZE = 250


class MaintenanceManager(models.Manager):
  """Perform maintenance tasks related to Transaction models."""

  def rebuild_inventory_table(self, confirm=False):
    """Wipe and rebuild the inventory table based on transaction data.

    :param confirm: A boolean indicating you REALLY want to do this
    :type confirm: bool

    :raises: :class:`panic.kitchen.exceptions.ConfirmationNeeded`
    """
    if not confirm:
      raise ConfirmationRequired("Are you sure you want to do this?")

    Inventory.objects.all().delete()

    all_transactions = super().get_queryset().all().order_by('datetime')
    paginator = Paginator(all_transactions, TRANSACTION_PAGE_SIZE)

    for page_number in paginator.page_range:
      page = paginator.page(page_number)

      for transaction in page.object_list:
        Inventory.objects.adjust(transaction)
