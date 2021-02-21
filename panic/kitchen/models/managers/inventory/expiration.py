"""Inventory Expiration manager."""

from datetime import timedelta

import pendulum
import pytz
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncDay


class ExpirationManager(models.Manager):
  """Retrieve Inventory expiration data for individual items."""

  def _get_inventory_expiry(self, inventory):
    """Return the expiry datetime of an inventory entry, for the user.

    Best before dates are generally accurate to "date" only, so the calculated
    expiry datetime is adjusted to the start of the user's local timezone day.

    :returns: A datetime, or None if no items are expiring.
    :rtype: None, :class:`datetime.datetime`
    """
    transaction_datetime = inventory.transaction.datetime
    shelf_life = inventory.item.shelf_life
    user_timezone = inventory.item.user.timezone

    user_time = pendulum.instance(
        transaction_datetime.astimezone(user_timezone) +
        timedelta(days=shelf_life)
    )
    return user_time.start_of('day').astimezone(pytz.utc)

  def get_inventory_expiration_datetime(self, item):
    """Return a date when which inventory older than are expired.

    Best before dates are generally accurate to "date" only, so the calculated
    expiry datetime is adjusted to the start of the user's local timezone day.

    :param item: A item instance to analyze
    :type item: :class:`kitchen.models.item.Item`

    :returns: A datetime, or None if no items are expiring.
    :rtype: None, :class:`datetime.datetime`
    """
    shelf_life = item.shelf_life
    timezone = item.user.timezone
    current_day_start = pendulum.now(tz=timezone).start_of('day')
    return current_day_start - timedelta(days=shelf_life)

  def get_next_expiry_datetime(self, item):
    """Return the datetime of the next expiring item(s), if any.

    Best before dates are generally accurate to "date" only, so the calculated
    expiry datetime is adjusted to the start of the user's local timezone day.

    :param item: A item instance to analyze
    :type item: :class:`kitchen.models.item.Item`

    :returns: A datetime, or None if no items are expiring.
    :rtype: None, :class:`datetime.datetime`
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
      next_expiry_date = next_expiry_datetime

    return next_expiry_date

  def get_next_expiry_quantity(self, item):
    """Return the quantity of the item(s) expiring next, if any.

    Best before dates are generally accurate to "date" only, so the calculated
    expiry datetime is adjusted to the start of the user's local timezone day.

    :param item: A item instance to analyze
    :type item: :class:`kitchen.models.item.Item`

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
          datetime=TruncDay(
            'transaction__datetime',
            tzinfo=timezone,
          ),
        ).\
        values('datetime',).\
        annotate(
          quantity=Sum('remaining')
        ).\
        order_by('datetime').\
        first()

    if next_quantity_sum:
      next_expiration_quantity = next_quantity_sum['quantity']
    return next_expiration_quantity

  def get_expired(self, item):
    """Return the total quantity of the specified item that is expired.

    Best before dates are generally accurate to "date" only, so the calculated
    expiry datetime is adjusted to the start of the user's local timezone day.

    :param item: A item instance to analyze
    :type item: :class:`kitchen.models.item.Item`

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
