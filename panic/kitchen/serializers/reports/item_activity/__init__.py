"""Serializer for the Item's activity report."""

import pytz
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from ....models.item import Item
from .item_activity_recent import RecentActivitySerializer

DEFAULT_TIMEZONE = pytz.utc.zone


class ItemActivityReportSerializer(serializers.ModelSerializer):
  """Serializer for the Item's activity report."""

  activity_first = serializers.ReadOnlyField(read_only=True)
  usage_total = serializers.ReadOnlyField(read_only=True)
  usage_avg_week = serializers.ReadOnlyField(read_only=True)
  usage_avg_month = serializers.ReadOnlyField(read_only=True)
  recent_activity = serializers.SerializerMethodField(read_only=True)

  class Meta:
    model = Item
    fields = (
        "activity_first",
        "usage_total",
        "usage_avg_week",
        "usage_avg_month",
        "recent_activity",
    )

  @swagger_serializer_method(serializer_or_field=RecentActivitySerializer)
  def get_recent_activity(self, obj):
    """Retrieve recent purchase/usage activity for an item."""
    return RecentActivitySerializer(obj).data
