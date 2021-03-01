"""Serializer for the store model."""

from rest_framework import serializers

from ..models.store import Store
from .bases import KitchenBaseModelSerializer


class StoreSerializer(KitchenBaseModelSerializer):
  """Serializer for Store."""

  user = serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model = Store
    exclude = ('_index',)
    read_only_fields = ("id",)

  def validate_name(self, name):
    """Ensure the name is unique (regardless of case) per user.

    :param name: The store name.
    :type name: str

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    self.case_unique_validator(name, "name")
    return name
