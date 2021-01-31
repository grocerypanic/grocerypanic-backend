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


class TransactionConsumptionHistorySerializer(serializers.Serializer):
  """Serializer for Transaction Consumption History"""
  id = serializers.IntegerField(write_only=True)
  consumption_last_two_weeks = serializers.SerializerMethodField(read_only=True)
  first_consumption_date = serializers.SerializerMethodField(read_only=True)
  total_consumption = serializers.SerializerMethodField(read_only=True)

  def get_consumption_last_two_weeks(self, obj):
    user_id = self.context['request'].user.id
    item_id = obj.id
    query = Transaction.consumption.get_last_two_weeks(item_id, user_id)
    return TransactionSerializer(query, many=True).data

  def get_first_consumption_date(self, obj):
    user_id = self.context['request'].user.id
    item_id = obj.id
    return Transaction.consumption.get_first_consumption(item_id, user_id)

  def get_total_consumption(self, obj):
    user_id = self.context['request'].user.id
    item_id = obj.id
    return Transaction.consumption.get_total_consumption(item_id, user_id)

  def update(self, instance, validated_data):
    pass

  def create(self, validated_data):
    pass
