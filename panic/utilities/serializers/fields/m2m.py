"""Serializer fields for M2M models."""

from rest_framework import serializers


class M2MThroughSerializerField(serializers.RelatedField):
  """Serializer field for M2M through models with original M2M functionality.

  This field will deserialize a list of `pk`'s, and serialize data in this
  format as well.
  """

  def to_internal_value(self, data):
    """Transform the *incoming* primitive data into a native value."""
    if isinstance(data, (
        int,
        str,
    )):
      return self.queryset.get(pk=data)
    return data

  def to_representation(self, value):
    """Transform the *outgoing* native value into primitive data."""
    return value.id
