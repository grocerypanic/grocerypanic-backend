"""Serializer for the Transaction Model"""

from rest_framework import serializers

from ..models.transaction import Transaction


class TransactionSerializer(serializers.ModelSerializer):
  """Serializer for Transactions"""
  user = serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model = Transaction
    fields = '__all__'
    read_only_fields = ("id", "date")
