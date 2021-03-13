"""Serializer for the user's recent activity."""

import pytz
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from ....models.item import Item
from .item_activity_last_two_weeks import LastTwoWeeksActivitySerializer

DEFAULT_TIMEZONE = pytz.utc.zone


class RecentActivitySerializer(serializers.ModelSerializer):
  """Serializer for the user's recent activity."""

  user_timezone = serializers.SerializerMethodField(read_only=True)
  usage_current_week = serializers.ReadOnlyField(read_only=True)
  usage_current_month = serializers.ReadOnlyField(read_only=True)
  activity_last_two_weeks = LastTwoWeeksActivitySerializer(
      many=True,
      read_only=True,
  )

  class Meta:
    model = Item
    fields = (
        "user_timezone",
        "usage_current_week",
        "usage_current_month",
        "activity_last_two_weeks",
    )

  @swagger_serializer_method(serializer_or_field=TimeZoneSerializerField)
  def get_user_timezone(self, obj):
    """Retrieve the user's configured timezone."""
    return obj.user.timezone.zone
