"""Transaction Activity model manager."""

from datetime import timedelta

import pendulum
import pytz
from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncDate, TruncDay


class ActivityManager(models.Manager):
  """Provide reporting on the usage activity patterns of Items."""

  def get_activity_first(self, item_id, zone=pytz.utc.zone):
    """Search for the first transaction for this item, and return the datetime.
    The datetime is returned in the specified timezone.

    This identifies the start datetime of all activity for this particular item.

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
          item=item_id,
        ).\
        values('datetime').\
        order_by('datetime').\
        first()
    if query_set:
      return query_set['datetime'].astimezone(zone)
    return None

  def get_activity_last_two_weeks(self, item_id, zone=pytz.utc.zone):
    """Retrieve the last two weeks of transaction activity.
    The activity is summed by each timezone adjusted day.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: A queryset representing the activity
    :rtype: :class:`django.db.models.QuerySet`, None
    """
    timezone_object = pytz.timezone(zone)
    query = self._query_activity_last_two_weeks(item_id, timezone_object)
    results = self._zfill_activity_last_two_weeks(query, timezone_object)
    return results

  def _query_activity_last_two_weeks(self, item_id, timezone_object):
    """Retrieve transaction activity for the past two weeks."""
    results = []

    start_of_window = pendulum.now(tz=timezone_object)
    end_of_window = (
        start_of_window -
        (timedelta(days=int(settings.TRANSACTION_HISTORY_MAX)))
    ).astimezone(timezone_object).start_of("day")

    query = super().get_queryset().\
        filter(
          item=item_id,
          datetime__date__gte=end_of_window,
        ).\
        order_by('-datetime').\
        annotate(date=TruncDate(TruncDay('datetime', tzinfo=timezone_object))).\
        values('date').\
        order_by('-date').\
        annotate(change=Sum('quantity'))

    if query:
      results = query

    return results

  def _zfill_activity_last_two_weeks(self, query_results, timezone_object):
    """Add zero `change` entries to the query for days without activity."""
    zero_padded_results = []
    query_hash = {}
    current_datetime = pendulum.now(timezone_object)

    for row in query_results:
      query_hash[row['date']] = row['change']

    for day in range(0, int(settings.TRANSACTION_HISTORY_MAX + 1)):
      history_date = (current_datetime - timedelta(days=day))\
          .start_of('day')\
          .date()
      zero_padded_results.append({
          'date': history_date,
          'change': query_hash.setdefault(history_date, 0),
      })

    return zero_padded_results

  def get_usage_current_week(self, item_id, zone=pytz.utc.zone):
    """Retrieve the sum of the current week of transaction activity.
    Week bounds are determined by the specified timezone.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: The total count of cumulative consumption
    :rtype: float
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

  def get_usage_current_month(self, item_id, zone=pytz.utc.zone):
    """Retrieve the sum of the current month of transaction activity.
    Week bounds are determined by the specified timezone.

    :param item_id: The pk of the item model instance in question
    :type item_id: int
    :param zone: A world timezone descriptor string (defaults to UTC)
    :type item_id: str

    :returns: The total count of cumulative consumption
    :rtype: float
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

  def get_usage_total(self, item_id):
    """Calculate the total sum consumption of an item.

    :param item_id: The pk of the item model instance in question
    :type item_id: int

    :returns: The total count of cumulative consumption
    :rtype: float
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
