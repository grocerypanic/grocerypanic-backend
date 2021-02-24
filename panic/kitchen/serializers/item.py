"""Serializer for the item model."""

import pytz
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models.item import Item
from . import DUPLICATE_OBJECT_MESSAGE
from .bases import RelatedValidatorModelSerializer

DEFAULT_TIMEZONE = pytz.utc.zone

READABLE_FIELDS = (
    'id',
    'expired',
    'has_partial_quantities',
    'name',
    'next_expiry_date',
    'next_expiry_datetime',
    'next_expiry_quantity',
    'price',
    'preferred_stores',
    'quantity',
    'shelf',
    'shelf_life',
)


class ItemSerializer(RelatedValidatorModelSerializer):
  """Serializer for Item."""

  user = serializers.HiddenField(default=serializers.CurrentUserDefault())
  next_expiry_date = serializers.ReadOnlyField()
  next_expiry_datetime = serializers.ReadOnlyField()
  next_expiry_quantity = serializers.ReadOnlyField()
  expired = serializers.ReadOnlyField()

  class Meta:
    model = Item
    exclude = (
        'index',
        '_next_expiry_quantity',
        '_expired',
    )
    read_only_fields = (
        "id",
        "expired",
        "next_expiry_date",
        "next_expiry_datetime",
        "next_expiry_quantity",
        "quantity",
    )
    validators = [
        UniqueTogetherValidator(
            queryset=Item.objects.all(),
            fields=['user', 'name'],
            message=DUPLICATE_OBJECT_MESSAGE
        )
    ]

  def validate_preferred_stores(self, preferred_stores):
    """Ensure preferred_stores are owned by the current request user.

    :param preferred_stores: A iterable of Store models.
    :type preferred_stores: List[:class:`panic.kitchen.models.store.Store`]

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    self.related_validator(preferred_stores, "preferred_stores")
    return preferred_stores

  def validate_shelf(self, shelf):
    """Ensure shelf is owned by the current request user.

    :param shelf: A related shelf instance for this model.
    :type shelf: :class:`panic.kitchen.models.shelf.Shelf`

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    self.related_validator(shelf, "shelf")
    return shelf
