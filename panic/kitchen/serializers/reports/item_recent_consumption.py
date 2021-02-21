"""Serializer for the user's recent consumption report."""

import pytz
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from ...models.item import Item
from ...models.transaction import Transaction
from .item_history import ItemHistorySerializer

DEFAULT_TIMEZONE = pytz.utc.zone


class RecentConsumptionSerializer(serializers.ModelSerializer):
  """Serializer for the user's recent consumption report."""

  user_timezone = serializers.SerializerMethodField(read_only=True)
  past_week = serializers.SerializerMethodField(read_only=True)
  past_month = serializers.SerializerMethodField(read_only=True)
  daily_past_two_weeks = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Item
    fields = (
        "user_timezone",
        "past_week",
        "past_month",
        "daily_past_two_weeks",
    )

  @swagger_serializer_method(serializer_or_field=TimeZoneSerializerField)
  def get_user_timezone(self, obj):
    """Report the user's configured timezone."""
    return obj.user.timezone.zone

  @swagger_serializer_method(
      serializer_or_field=ItemHistorySerializer(many=True)
  )
  def get_daily_past_two_weeks(self, obj):
    """Trigger the transaction consumption report for the past two weeks."""
    item_id = obj.id
    configured_timezone = obj.user.timezone.zone

    query = Transaction.objects.get_last_two_weeks(
        item_id,
        configured_timezone,
    )
    return ItemHistorySerializer(query, many=True).data

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_past_month(self, obj):
    """Trigger the transaction consumption report for the current month."""
    item_id = obj.id
    configured_timezone = obj.user.timezone.zone
    return Transaction.objects.get_current_month_consumption(
        item_id,
        configured_timezone,
    )

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_past_week(self, obj):
    """Trigger the transaction consumption report for the current week."""
    item_id = obj.id
    configured_timezone = obj.user.timezone.zone
    return Transaction.objects.get_current_week_consumption(
        item_id,
        configured_timezone,
    )
