"""Item model."""

import pendulum
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.functional import cached_property

from . import constants
from .inventory import Inventory
from .managers.item import ItemManager
from .mixins import (
    FullCleanMixin,
    RelatedFieldEnforcementMixin,
    UniqueNameConstraintMixin,
)
from .transaction import Transaction
from naturalsortfield import NaturalSortField
from spa_security.fields import BlondeCharField
from utilities.models.decorators.caching import PersistentCachedProperty

User = get_user_model()


class Item(
    FullCleanMixin,
    UniqueNameConstraintMixin,
    RelatedFieldEnforcementMixin,
    models.Model,
):
  """Item model."""

  MAXIMUM_NAME_LENGTH = 255
  MINIMUM_SHELF_LIFE = 1
  MAXIMUM_SHELF_LIFE = 365 * 3
  DEFAULT_SHELF_LIFE = 7

  has_partial_quantities = models.BooleanField(default=False)
  name = BlondeCharField(max_length=MAXIMUM_NAME_LENGTH)
  preferred_stores = models.ManyToManyField(
      'Store', through='kitchen.PreferredStore'
  )
  price = models.DecimalField(max_digits=10, decimal_places=2)
  quantity = models.FloatField(
      default=0,
      validators=[
          MinValueValidator(constants.MINIMUM_QUANTITY),
          MaxValueValidator(constants.MAXIMUM_QUANTITY),
      ],
  )
  shelf = models.ForeignKey(
      'Shelf', on_delete=models.RESTRICT, blank=True, null=True
  )
  shelf_life = models.IntegerField(
      default=DEFAULT_SHELF_LIFE,
      validators=[
          MinValueValidator(MINIMUM_SHELF_LIFE),
          MaxValueValidator(MAXIMUM_SHELF_LIFE),
      ],
  )
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  _expired = models.FloatField(
      null=True,
      blank=True,
      default=None,
      validators=[
          MinValueValidator(constants.MINIMUM_QUANTITY),
          MaxValueValidator(constants.MAXIMUM_QUANTITY),
      ],
  )
  _index = NaturalSortField(
      for_field="name",
      max_length=MAXIMUM_NAME_LENGTH,
  )
  _next_expiry_quantity = models.FloatField(
      null=True,
      blank=True,
      default=None,
      validators=[
          MinValueValidator(constants.MINIMUM_QUANTITY),
          MaxValueValidator(constants.MAXIMUM_QUANTITY),
      ],
  )

  objects = ItemManager()

  class Meta:
    indexes = [
        models.Index(fields=['_index']),
    ]

  @cached_property
  def activity_first(self):
    """Search for the first transaction for this item, and return the datetime.
    The returned datetime is in in UTC.

    :returns: The datetime, or None
    :rtype: :class:`datetime.datetime`, None
    """
    return Transaction.objects.get_activity_first(self.id,)

  @property
  def activity_last_two_weeks(self):
    """Retrieve the last two weeks of transaction activity.
    The activity is summed by each timezone adjusted day.

    :returns: A queryset representing the activity
    :rtype: :class:`django.db.models.QuerySet`, None
    """
    return Transaction.objects.get_activity_last_two_weeks(
        self.id, zone=self.user.timezone.zone
    )

  @PersistentCachedProperty(ttl_field="next_expiry_datetime")
  def expired(self):
    """Return the sum quantity of all inventory that is expired.

    :returns: The quantity of items that will expire next
    :rtype: float
    """
    return Inventory.objects.get_expired(self)

  @property
  def next_expiry_date(self):
    """Return the date of the next batch of expiring items, if any.

    The date is tz corrected to the User's configured tz.

    :returns: A date, or None if no items are expiring.
    :rtype: None, :class:`datetime.date`
    """
    user_date = None

    # pylint: disable=using-constant-test
    utc_datetime = self.next_expiry_datetime

    if utc_datetime:
      user_date = utc_datetime.astimezone(self.user.timezone).date()
    return user_date

  @cached_property
  def next_expiry_datetime(self):
    """Return the datetime of the next batch of expiring items, if any.

    The datetime is corrected to the User's start of tz day.

    :returns: A date, or None if no items are expiring.
    :rtype: None, :class:`datetime.date`
    """
    return Inventory.objects.get_next_expiry_datetime(self)

  @PersistentCachedProperty(ttl_field="next_expiry_datetime")
  def next_expiry_quantity(self):
    """Return the quantity of the next batch of expiring items, if any.

    The items are aggregated by the user's timezone based date.

    :returns: The quantity of items that will expire next
    :rtype: float
    """
    return Inventory.objects.get_next_expiry_quantity(self)

  @property
  def usage_avg_week(self):
    """Retrieve an item's average weekly usage, since it's first activity.

    :returns: The average usage
    :rtype: float
    """
    activity_first = self.activity_first
    average = 0
    if activity_first is not None:
      since_first_transaction = (
          pendulum.now() - pendulum.instance(activity_first)
      )
      average = self.usage_total / (since_first_transaction.in_weeks() + 1)
    return float("{:.2f}".format(average))

  @property
  def usage_avg_month(self):
    """Retrieve an item's average monthly usage, since it's first activity.

    :returns: The average usage
    :rtype: float
    """
    activity_first = self.activity_first
    average = 0
    if activity_first is not None:
      since_first_transaction = (
          pendulum.now() - pendulum.instance(activity_first)
      )
      average = self.usage_total / (since_first_transaction.in_months() + 1)
    return float("{:.2f}".format(average))

  @property
  def usage_current_week(self):
    """Retrieve the sum of the current week of transaction activity.
    Week bounds are determined by the specified timezone.

    :returns: The total count of cumulative consumption
    :rtype: float
    """
    return Transaction.objects.get_usage_current_week(
        self.id, zone=self.user.timezone.zone
    )

  @property
  def usage_current_month(self):
    """Retrieve the sum of the current month of transaction activity.
    Month bounds are determined by the specified timezone.

    :returns: The total count of cumulative consumption
    :rtype: float
    """
    return Transaction.objects.get_usage_current_month(
        self.id, zone=self.user.timezone.zone
    )

  @cached_property
  def usage_total(self):
    """Calculate the total sum consumption of an item.

    :returns: The total count of cumulative consumption
    :rtype: float
    """
    return Transaction.objects.get_usage_total(self.id)

  def __str__(self):
    return str(self.name)

  def invalidate_caches(self):
    """Clear all types of cached properties."""
    for key, value in self.__class__.__dict__.items():
      if isinstance(value, (
          PersistentCachedProperty,
          cached_property,
      )):
        try:
          delattr(self, key)
        except AttributeError:
          pass

  def clean(self):
    """Clean model."""
    super().clean()
    fields = ["shelf"]
    self.related_validator(fields)
