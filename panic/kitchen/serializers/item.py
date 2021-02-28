"""Serializer for the item model."""

import pytz
from rest_framework import serializers

from ..models.item import Item
from .bases import KitchenBaseModelSerializer

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


class ItemSerializer(KitchenBaseModelSerializer):
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

  def validate_name(self, name):
    """Ensure the name is unique (regardless of case) per user.

    :param name: The item name.
    :type name: str

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    self.case_unique_validator(name, "name")
    return name

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
