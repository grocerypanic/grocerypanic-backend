"""Serializer fields for M2M models."""

from typing import Union, cast

from django.db.models import Model
from rest_framework import serializers


class M2MThroughSerializerField(serializers.RelatedField):  # type: ignore
  """Serializer field for M2M through models with original M2M functionality.

  This field will deserialize a list of `pk`'s, and serialize data in this
  format as well.
  """

  def to_internal_value(self, data: Union[int, str, Model]) -> Model:
    """Transform the *incoming* primitive data into a native value."""
    if isinstance(data, (
        int,
        str,
    )):
      return cast(Model, self.queryset.get(pk=data))
    return data

  def to_representation(self, value: Model) -> int:
    """Transform the *outgoing* native value into primitive data."""
    return value.id  # type: ignore
