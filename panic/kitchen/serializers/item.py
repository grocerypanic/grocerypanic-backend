"""Serializer for the Item Model"""

import pytz
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from ..models.item import Item
from ..models.transaction import Transaction
from . import DUPLICATE_OBJECT_MESSAGE

DEFAULT_TIMEZONE = pytz.utc.zone


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


class ItemHistorySerializer(serializers.Serializer):
  """Serializer for Item History"""
  date = serializers.DateField(read_only=True)
  quantity = serializers.IntegerField(read_only=True)

  def create(self, validated_data):
    pass

  def update(self, instance, validated_data):
    pass


class ItemConsumptionHistorySerializer(serializers.ModelSerializer):
  """Serializer for Item Consumption History"""
  timezone = serializers.CharField(
      write_only=True,
      max_length=255,
      default=DEFAULT_TIMEZONE,
  )
  consumption_last_two_weeks = serializers.SerializerMethodField(read_only=True)
  first_consumption_date = serializers.SerializerMethodField(read_only=True)
  total_consumption = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Item
    fields = (
        "timezone",
        "consumption_last_two_weeks",
        "first_consumption_date",
        "total_consumption",
    )

  def get_initial_timezone_value(self):
    timezone_value = self.initial_data.get('timezone', DEFAULT_TIMEZONE)
    return timezone_value

  def validate_timezone(self, value):
    try:
      pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
      raise serializers.ValidationError({
          'timezone': "Please provide a valid timezone string."
      })

  @swagger_serializer_method(
      serializer_or_field=ItemHistorySerializer(many=True)
  )
  def get_consumption_last_two_weeks(self, obj):
    item_id = obj.id
    configured_timezone = self.get_initial_timezone_value()
    query = Transaction.consumption.get_last_two_weeks(
        item_id,
        configured_timezone,
    )
    return ItemHistorySerializer(query, many=True).data

  @swagger_serializer_method(serializer_or_field=serializers.DateTimeField)
  def get_first_consumption_date(self, obj):
    item_id = obj.id
    configured_timezone = self.get_initial_timezone_value()
    return Transaction.consumption.get_first_consumption(
        item_id,
        configured_timezone,
    )

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_total_consumption(self, obj):
    item_id = obj.id
    return Transaction.consumption.get_total_consumption(item_id)
