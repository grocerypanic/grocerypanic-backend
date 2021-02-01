"""Serializer for the Item Model"""

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models.item import Item
from ..models.transaction import Transaction
from . import DUPLICATE_OBJECT_MESSAGE
from .transaction import TransactionSerializer


class ItemSerializer(serializers.ModelSerializer):
  """Serializer for Item"""
  user = serializers.HiddenField(default=serializers.CurrentUserDefault())

  class Meta:
    model = Item
    exclude = ('index',)
    read_only_fields = (
        "id",
        "next_expiry_date",
        "next_expiry_quantity",
        "expired",
    )
    validators = [
        UniqueTogetherValidator(
            queryset=Item.objects.all(),
            fields=['user', 'name'],
            message=DUPLICATE_OBJECT_MESSAGE
        )
    ]


class ItemConsumptionHistorySerializer(serializers.ModelSerializer):
  """Serializer for Transaction Consumption History"""
  consumption_last_two_weeks = serializers.SerializerMethodField(read_only=True)
  first_consumption_date = serializers.SerializerMethodField(read_only=True)
  total_consumption = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Item
    fields = (
        "consumption_last_two_weeks",
        "first_consumption_date",
        "total_consumption",
    )

  def get_consumption_last_two_weeks(self, obj):
    item_id = obj.id
    query = Transaction.consumption.get_last_two_weeks(item_id)
    return TransactionSerializer(query, many=True).data

  def get_first_consumption_date(self, obj):
    item_id = obj.id
    return Transaction.consumption.get_first_consumption(item_id)

  def get_total_consumption(self, obj):
    item_id = obj.id
    return Transaction.consumption.get_total_consumption(item_id)
