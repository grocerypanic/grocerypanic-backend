"""Timezones serializer."""

from rest_framework import serializers


class TimezoneSerializer(serializers.Serializer):
  """Timezones serializer."""

  id = serializers.IntegerField()  # pylint: disable=invalid-name
  name = serializers.StringRelatedField()

  # pylint: disable=useless-super-delegation
  def create(self, validated_data):
    """Implement ABC."""
    return super().create(validated_data)

  # pylint: disable=useless-super-delegation
  def update(self, instance, validated_data):
    """Implement ABC."""
    return super().update(instance, validated_data)
