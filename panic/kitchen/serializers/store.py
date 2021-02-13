"""Serializer for the store model."""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models.store import Store
from . import DUPLICATE_OBJECT_MESSAGE


class StoreSerializer(serializers.ModelSerializer):
  """Serializer for Store."""

  user = serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model = Store
    exclude = ('index',)
    read_only_fields = ("id",)
    validators = [
        UniqueTogetherValidator(
            queryset=Store.objects.all(),
            fields=['user', 'name'],
            message=DUPLICATE_OBJECT_MESSAGE
        )
    ]
