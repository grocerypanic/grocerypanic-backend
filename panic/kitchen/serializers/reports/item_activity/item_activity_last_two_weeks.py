"""Serializer for an Item's last two weeks of usage activity."""

from rest_framework import serializers


class LastTwoWeeksActivitySerializer(serializers.Serializer):
  """Serializer for an Item's last two weeks of usage activity."""

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
