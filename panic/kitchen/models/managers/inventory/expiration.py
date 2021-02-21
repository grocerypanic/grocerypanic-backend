"""Inventory Expiration manager."""

from datetime import timedelta

import pendulum
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncDate


class ExpirationManager(models.Manager):
  """Retrieve Inventory expiration data for individual items."""

  def _get_inventory_expiry(self, inventory):
    """Return the expiry date of an inventory entry.

    The date is tz corrected to the User's configured tz.

    :returns: A datetime, or None if no items are expiring.
    :rtype: None, :class:`datetime.datetime`
    """
    transaction_datetime = inventory.transaction.datetime
    shelf_life = inventory.item.shelf_life
    user_timezone = inventory.item.user.timezone

    utc_time = transaction_datetime + timedelta(days=shelf_life)
    return utc_time.astimezone(user_timezone)

  def get_inventory_expiration_datetime(self, item):
    """Return a date when which inventory older than are expired.
    The datetime is tz corrected to the User's configured tz.

    :param item: A item instance to analyze
    :type item: :class:`kichen.models.item.Item`

    :returns: A datetime, or None if no items are expiring.
    :rtype: None, :class:`datetime.datetime`
    """
    shelf_life = item.shelf_life
    timezone = item.user.timezone
    current_day_start = pendulum.now(tz=timezone).start_of('day')
    return current_day_start - timedelta(days=shelf_life)

  def get_next_expiry_date(self, item):
    """Return the date of the next expiring item(s), if any.
    The date is tz corrected to the User's configured tz.

    :param item: A item instance to analyze
    :type item: :class:`kichen.models.item.Item`

    :returns: A date, or None if no items are expiring.
    :rtype: None, :class:`datetime.date`
    """
    next_expiry_date = None
    inventory_expiration = self.get_inventory_expiration_datetime(item)

    oldest_inventory = super().get_queryset().\
        filter(
          item=item,
          transaction__datetime__gte=inventory_expiration,
        ).\
        order_by(
        'transaction__datetime'
        ).\
        first()

    if oldest_inventory:
      next_expiry_datetime = self._get_inventory_expiry(oldest_inventory)
      next_expiry_date = next_expiry_datetime.date()

    return next_expiry_date

  def get_next_expiry_quantity(self, item):
    """Return the quantity of the item(s) expiring next, if any.
    The date is tz corrected to the User's configured tz.

    :param item: A item instance to analyze
    :type item: :class:`kichen.models.item.Item`

    :returns: A quantity expressed as a float
    :rtype: float
    """
    next_expiration_quantity = 0
    inventory_expiration = self.get_inventory_expiration_datetime(item)
    timezone = item.user.timezone

    next_quantity_sum = super().get_queryset().\
        filter(
          item=item,
          transaction__datetime__gte=inventory_expiration,
        ).\
        annotate(
          date=TruncDate(
            'transaction__datetime',
            tzinfo=timezone,
          ),
        ).\
        values('date',).\
        annotate(
          quantity=Sum('remaining')
        ).\
        order_by('date').\
        first()

    if next_quantity_sum:
      next_expiration_quantity = next_quantity_sum['quantity']
    return next_expiration_quantity

  def get_expired(self, item):
    """Return the total quantity of the specified item that is expired.

    :param item: A item instance to analyze
    :type item: :class:`kichen.models.item.Item`

    :returns: A quantity expressed as a float
    :rtype: float
    """
    expired = 0
    inventory_expiration = self.get_inventory_expiration_datetime(item)

    total_expired_inventory = super().get_queryset().\
        filter(
          item=item, transaction__datetime__lt=inventory_expiration
        ).\
        values('remaining').\
        aggregate(
          quantity=Sum('remaining')
        )['quantity']

    if total_expired_inventory:
      expired = total_expired_inventory
    return expired
