"""Serializer for the Transaction Model"""

from rest_framework import serializers

from ..models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):
  """Serializer for Transactions"""

  class Meta:
    model = Transaction
    fields = '__all__'
    read_only_fields = ("id", "date")

  def validate_item(self, value):
    user = self.context['request'].user
    if value.user != user:
      raise serializers.ValidationError({
          'item': "Please provide a valid item."
      })
    return value
