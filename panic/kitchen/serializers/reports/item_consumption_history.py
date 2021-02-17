"""Serializer for the item consumption report."""

import pytz
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from ...models.item import Item
from ...models.transaction import Transaction
from .item_history import ItemHistorySerializer

DEFAULT_TIMEZONE = pytz.utc.zone


class ItemConsumptionHistorySerializer(serializers.ModelSerializer):
  """Serializer for Item Consumption History."""

  timezone = serializers.CharField(
      write_only=True,
      max_length=255,
      default=DEFAULT_TIMEZONE,
  )
  consumption_last_two_weeks = serializers.SerializerMethodField(read_only=True)
  consumption_this_month = serializers.SerializerMethodField(read_only=True)
  consumption_this_week = serializers.SerializerMethodField(read_only=True)
  first_consumption_date = serializers.SerializerMethodField(read_only=True)
  total_consumption = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Item
    fields = (
        "timezone",
        "consumption_last_two_weeks",
        "consumption_this_month",
        "consumption_this_week",
        "first_consumption_date",
        "total_consumption",
    )

  def validate_timezone(self, value):
    """Ensure the timezone field is a valid timezone string.

    :param value: The value expected to be a valid timezone string
    :type value: str

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    try:
      pytz.timezone(value)
    except pytz.exceptions.UnknownTimeZoneError:
      raise serializers.ValidationError(
          detail="Please provide a valid timezone string.",
      )

  @swagger_serializer_method(
      serializer_or_field=ItemHistorySerializer(many=True)
  )
  def get_consumption_last_two_weeks(self, obj):
    """Trigger the transaction consumption report for the past two weeks."""
    item_id = obj.id
    configured_timezone = self.__get_initial_timezone_value()
    query = Transaction.objects.get_last_two_weeks(
        item_id,
        configured_timezone,
    )
    return ItemHistorySerializer(query, many=True).data

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_consumption_this_month(self, obj):
    """Trigger the transaction consumption report for the current month."""
    item_id = obj.id
    configured_timezone = self.__get_initial_timezone_value()
    return Transaction.objects.get_current_month_consumption(
        item_id,
        configured_timezone,
    )

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_consumption_this_week(self, obj):
    """Trigger the transaction consumption report for the current week."""
    item_id = obj.id
    configured_timezone = self.__get_initial_timezone_value()
    return Transaction.objects.get_current_week_consumption(
        item_id,
        configured_timezone,
    )

  @swagger_serializer_method(serializer_or_field=serializers.DateTimeField)
  def get_first_consumption_date(self, obj):
    """Retrieve the first consumption date for this item, if any."""
    item_id = obj.id
    configured_timezone = self.__get_initial_timezone_value()
    return Transaction.objects.get_first_consumption(
        item_id,
        configured_timezone,
    )

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_total_consumption(self, obj):
    """Trigger the transaction consumption report for total consumption."""
    item_id = obj.id
    return Transaction.objects.get_total_consumption(item_id)

  def __get_initial_timezone_value(self):
    timezone_value = self.initial_data.get('timezone', DEFAULT_TIMEZONE)
    return timezone_value
