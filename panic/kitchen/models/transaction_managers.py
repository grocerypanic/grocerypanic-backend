"""Inventory Transaction Model Managers"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils.timezone import now


class ItemExpirationCalculator:
  """Handles expiration calculations and updates to the associated models.

  :param item: An instance of the model Item
  :type item: :class:`panic.kitchen.models.items.Item`
  """

  def __init__(self, item):
    self.quantity = item.quantity
    self.oldest = now()
    self.expired = 0
    self.next_to_expire = 0
    self.item = item

  def __update_oldest_expiry(self):
    """If there is no quantity of items marked upcoming for expiry, change the
    oldest date to the current timestamp."""

    if self.next_to_expire < 1:
      self.oldest = now()

  def __transaction_date_is_expired(self, transaction):
    """Compares an items transaction date to it's expiration date, to determine
    if the date of the transaction makes the item expired or not.

    :param transaction: An instance of the model Transactions
    :type transaction: :class:`panic.kitchen.models.transactions.Transaction`
    :return: A value indicating if the transaction items are expired
    :rtype: bool
    """

    item_expiry_date = (
        transaction.datetime.date() + timedelta(days=self.item.shelf_life)
    )
    if now().date() >= item_expiry_date:
      return True
    return False

  def __reconcile_consumption(self, transaction):
    """Handles a negative inventory change by debiting the calculated expiration
    total by the number of items consumed.

    :param transaction: An instance of the model Transactions
    :type transaction: :class:`panic.kitchen.models.transactions.Transaction`
    """

    self.expired += transaction.quantity

  def __reconcile_purchase(self, remaining_inventory_to_check, transaction):
    """Handles a positive inventory change, by either debiting the remaining
    count of items that need to be checked, or increasing the count of expired
    items (if those purchased items are already expired).

    :param remaining_inventory_to_check: The amount of inventory to reconcile
    :type remaining_inventory_to_check: int
    :param transaction: An instance of the model Transactions
    :type transaction: :class:`panic.kitchen.models.transactions.Transaction`
    :returns: The amount of inventory yet to be checked
    :rtype: int
    """

    self.oldest = transaction.datetime.date()
    remaining_inventory_to_check -= transaction.quantity

    if self.__transaction_date_is_expired(transaction):
      self.expired += transaction.quantity
    else:
      self.next_to_expire = min(
          remaining_inventory_to_check + transaction.quantity,
          transaction.quantity
      )
    return remaining_inventory_to_check

  def reconcile_transaction_history(self, transaction_history):
    """Iterates through an item's transaction history, updating it's expiry
    information to reconcile the current quantity with the date/time of each
    transaction.

    :param transaction_history: A queryset of the model Transaction
    :type transaction_history: :class:`django.db.models.query.QuerySet`
    """

    for record in transaction_history:
      remaining_inventory_to_check = self.reconcile_single_transaction(record)
      if remaining_inventory_to_check < 1:
        break
      self.quantity = remaining_inventory_to_check
    self.__update_oldest_expiry()

  def reconcile_single_transaction(self, transaction):
    """Processes an individual transaction from a reverse chronology, updating
    the data for expired inventory, and next inventory to expire.

    :returns: The amount of inventory yet to be reconciled
    :rtype: int
    """

    remaining_inventory_to_check = self.quantity

    if transaction.quantity > 0:
      remaining_inventory_to_check = self.__reconcile_purchase(
          remaining_inventory_to_check, transaction
      )
    else:
      self.__reconcile_consumption(transaction)

    return remaining_inventory_to_check

  def write_expiry_to_item_model(self):
    """Updates the associated item's expiry information from the calculated
    results."""

    self.item.next_expiry_quantity = self.next_to_expire
    self.item.next_expiry_date = (
        self.oldest + timedelta(days=self.item.shelf_life)
    )
    self.item.expired = max(self.expired, 0)


class ExpiryManager(models.Manager):
  """Adds Item expiry management features to the Transaction model."""

  def get_item_history(self, item):
    """Generate a query set representing an item's transaction history.

    :param item: An instance of the model Item
    :type item: :class:`panic.kitchen.models.items.Item`
    :returns: A queryset of the model Transaction containing this item
    :rtype: :class:`django.db.models.query.QuerySet`
    """

    return super().get_queryset().filter(item=item).order_by("-datetime")

  def update(self, transaction):
    """Updates the expiry data for an item associated to a transaction.

    :param transaction: An instance of the model Transactions
    :type transaction: :class:`panic.kitchen.models.transactions.Transaction`
    """

    calculator = ItemExpirationCalculator(transaction.item)

    if calculator.quantity > 0:
      item_history = self.get_item_history(calculator.item)
      calculator.reconcile_transaction_history(item_history)

    calculator.write_expiry_to_item_model()


class ConsumptionHistoryManager(models.Manager):

  def get_first_consumption(self, item_id, user_id):
    query_set = super().get_queryset().filter(
        quantity__lt=0,
        user=user_id,
        item=item_id,
    ).values('datetime').order_by('datetime').first()
    if query_set:
      return query_set['datetime']
    return None

  def get_last_two_weeks(self, item_id, user_id):
    start_of_window = now()
    end_of_window = start_of_window - timedelta(
        days=int(settings.TRANSACTION_HISTORY_MAX)
    )

    return super().get_queryset().filter(
        user=user_id,
        item=item_id,
        datetime__date__lte=start_of_window,
        datetime__date__gt=end_of_window
    ).order_by('-datetime')

  def get_total_consumption(self, item_id, user_id):
    quantity = super().get_queryset().filter(
        quantity__lt=0,
        user=user_id,
        item=item_id,
    ).aggregate(quantity=Sum('quantity'))['quantity']
    if quantity:
      return abs(quantity)
    return 0
