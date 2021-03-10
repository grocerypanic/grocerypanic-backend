"""Serializer for the Shelf model."""

from rest_framework import serializers

from ..models.shelf import Shelf
from .bases import KitchenBaseModelSerializer


class ShelfSerializer(KitchenBaseModelSerializer):
  """Serializer for Shelf."""

  user = serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model = Shelf
    exclude = ('_index',)
    read_only_fields = ("id",)

  def validate_name(self, name):
    """Ensure the name is unique (regardless of case) per user.

    :param name: The shelf name.
    :type name: str

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    self.case_unique_validator(name, "name")
    return name
