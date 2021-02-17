"""Inventory Transaction model managers."""

from datetime import timedelta

import pendulum
import pytz
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.utils.timezone import now


class ConsumptionHistoryManager(models.Manager):
  """Provide reporting on the consumption patterns of items."""

  def get_current_week_consumption(self, item_id, zone=pytz.utc.zone):
    """Retrieve the sum of the current week of transaction activity.
    Week bounds are determined by the specified timezone.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: The total count of cumulative consumption
    :rtype: int
    """
    start_of_week = pendulum.now(zone).start_of('week')

    quantity = super().get_queryset().\
        filter(
          item=item_id,
          quantity__lt=0,
          datetime__gte=start_of_week,
        ).\
        aggregate(quantity=Sum('quantity'))['quantity']

    if quantity:
      return abs(quantity)
    return 0

  def get_current_month_consumption(self, item_id, zone=pytz.utc.zone):
    """Retrieve the sum of the current month of transaction activity.
    Week bounds are determined by the specified timezone.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: The total count of cumulative consumption
    :rtype: int
    """
    start_of_month = pendulum.now(zone).start_of('month')

    quantity = super().get_queryset().\
        filter(
          item=item_id,
          quantity__lt=0,
          datetime__gte=start_of_month,
        ).\
        aggregate(quantity=Sum('quantity'))['quantity']

    if quantity:
      return abs(quantity)
    return 0

  def get_first_consumption(self, item_id, zone=pytz.utc.zone):
    """Search for the first transaction for this item, and returns the date.
    The date is calculated in the specified timezone.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: The datetime, or None
    :rtype: :class:`datetime.datetime`, None
    """
    zone = pytz.timezone(zone)
    query_set = super().get_queryset().\
        filter(
          quantity__lt=0,
          item=item_id,
        ).\
        values('datetime').\
        order_by('datetime').\
        first()
    if query_set:
      return query_set['datetime'].astimezone(zone)
    return None

  def get_last_two_weeks(self, item_id, zone=pytz.utc.zone):
    """Retrieve the last two weeks of transaction activity.
    The activity is summed by each timezone adjusted day.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: A queryset representing the activity
    :rtype: :class:`django.db.models.QuerySet`, None
    """
    zone = pytz.timezone(zone)
    start_of_window = now()
    end_of_window = (
        start_of_window.astimezone(zone) -
        timedelta(days=int(settings.TRANSACTION_HISTORY_MAX))
    )
    return super().get_queryset().\
        filter(
          item=item_id,
          datetime__date__gte=end_of_window.date(),
        ).\
        order_by('-datetime').\
        annotate(date=TruncDate('datetime', tzinfo=zone)).\
        values('date').annotate(quantity=Sum('quantity'))

  def get_total_consumption(self, item_id):
    """Calculate the total sum consumption of an item.

    :param item_id: The pk of the item model instance in question
    :type item_id: int

    :returns: The total count of cumulative consumption
    :rtype: int
    """
    quantity = super().get_queryset().\
        filter(
          quantity__lt=0,
          item=item_id,
        ).\
        aggregate(quantity=Sum('quantity'))['quantity']
    if quantity:
      return abs(quantity)
    return 0
