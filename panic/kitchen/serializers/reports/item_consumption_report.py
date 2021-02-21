"""Serializer for the item consumption report."""

import pytz
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from ...models.item import Item
from ...models.transaction import Transaction
from .item_recent_consumption import RecentConsumptionSerializer

DEFAULT_TIMEZONE = pytz.utc.zone


class ItemConsumptionHistoryReportSerializer(serializers.ModelSerializer):
  """Serializer for Item Consumption Report History."""

  first_consumption = serializers.SerializerMethodField(read_only=True)
  total_consumption = serializers.SerializerMethodField(read_only=True)
  recent_consumption = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Item
    fields = (
        "first_consumption",
        "total_consumption",
        "recent_consumption",
    )

  @swagger_serializer_method(serializer_or_field=RecentConsumptionSerializer)
  def get_recent_consumption(self, obj):
    """Retrieve the use consumption report."""
    return RecentConsumptionSerializer(obj).data

  @swagger_serializer_method(serializer_or_field=serializers.DateTimeField)
  def get_first_consumption(self, obj):
    """Retrieve the first consumption datetime for this item, if any."""
    item_id = obj.id
    return Transaction.objects.get_first_consumption(item_id)

  @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
  def get_total_consumption(self, obj):
    """Trigger the transaction consumption report for total consumption."""
    item_id = obj.id
    return Transaction.objects.get_total_consumption(item_id)
