"""Item model."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from naturalsortfield import NaturalSortField

from spa_security.fields import BlondeCharField
from . import constants
from .inventory import Inventory

User = get_user_model()


class Item(models.Model):
  """Item model."""

  MAXIMUM_NAME_LENGTH = 255
  MINIMUM_SHELF_LIFE = 1
  MAXIMUM_SHELF_LIFE = 365 * 3
  DEFAULT_SHELF_LIFE = 7

  has_partial_quantities = models.BooleanField(default=False)
  index = NaturalSortField(
      for_field="name",
      max_length=MAXIMUM_NAME_LENGTH,
  )  # Pagination Index
  name = BlondeCharField(max_length=MAXIMUM_NAME_LENGTH)
  preferred_stores = models.ManyToManyField('Store')
  price = models.DecimalField(max_digits=10, decimal_places=2)
  quantity = models.FloatField(
      default=0,
      validators=[
          MinValueValidator(constants.MINIMUM_QUANTITY),
          MaxValueValidator(constants.MAXIMUM_QUANTITY),
      ],
  )
  shelf = models.ForeignKey('Shelf', on_delete=models.CASCADE)
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
  _next_expiry_quantity = models.FloatField(
      null=True,
      blank=True,
      default=None,
      validators=[
          MinValueValidator(constants.MINIMUM_QUANTITY),
          MaxValueValidator(constants.MAXIMUM_QUANTITY),
      ],
  )

  objects = models.Manager()

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['user', 'name'], name='item per user')
    ]
    indexes = [
        models.Index(fields=['index']),
    ]

  @property
  def next_expiry_date(self):
    """Return the date of the next batch of expiring items, if any.

    The date is tz corrected to the User's configured tz.

    :returns: A date, or None if no items are expiring.
    :rtype: None, :class:`datetime.date`
    """
    user_date = None
    utc_datetime = Inventory.objects.get_next_expiry_datetime(self)
    if utc_datetime:
      user_date = utc_datetime.astimezone(self.user.timezone).date()
    return user_date

  @property
  def next_expiry_quantity(self):
    """Return the quantity of the next batch of expiring items, if any.

    The items are aggregated by the user's timezone based date.

    :returns: The quantity of items that will expire next
    :rtype: float
    """
    return Inventory.objects.get_next_expiry_quantity(self)

  @property
  def expired(self):
    """Return the sum quantity of all inventory that is expired.

    :returns: The quantity of items that will expire next
    :rtype: float
    """
    return Inventory.objects.get_expired(self)

  def __str__(self):
    return str(self.name)

  # pylint: disable=signature-differs
  def save(self, *args, **kwargs):
    """Clean and save model."""
    self.full_clean()
    return super(Item, self).save(*args, **kwargs)
