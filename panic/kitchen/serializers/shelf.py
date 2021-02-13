"""Serializer for the shelf model."""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models.shelf import Shelf
from . import DUPLICATE_OBJECT_MESSAGE


class ShelfSerializer(serializers.ModelSerializer):
  """Serializer for Shelf."""

  user = serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model = Shelf
    exclude = ('index',)
    read_only_fields = ("id",)
    validators = [
        UniqueTogetherValidator(
            queryset=Shelf.objects.all(),
            fields=['user', 'name'],
            message=DUPLICATE_OBJECT_MESSAGE
        )
    ]
