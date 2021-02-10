"""Serializer for the item history report."""

from rest_framework import serializers


class ItemHistorySerializer(serializers.Serializer):
  """Serializer for Item History."""

  date = serializers.DateField(read_only=True)
  quantity = serializers.IntegerField(read_only=True)

  # pylint: disable=useless-super-delegation
  def create(self, validated_data):
    """Implement ABC."""
    return super().create(validated_data)

  # pylint: disable=useless-super-delegation
  def update(self, instance, validated_data):
    """Implement ABC."""
    return super().update(instance, validated_data)
