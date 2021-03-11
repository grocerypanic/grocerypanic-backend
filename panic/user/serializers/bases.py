"""User model serializer base classes."""

from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from ..models.user import User
from .validators.user import validate_language


class UserBase(serializers.Serializer):
  """User model serializer base class with custom fields."""

  language_code = serializers.CharField(
      max_length=20,
      default=User.DEFAULT_LANGUAGE_CODE,
      validators=[validate_language],
  )
  has_profile_initialized = serializers.BooleanField(default=False)
  timezone = TimeZoneSerializerField(default=User.DEFAULT_TIMEZONE,)

  # pylint: disable=useless-super-delegation
  def create(self, validated_data):
    """Implement ABC."""
    return super().create(validated_data)

  # pylint: disable=useless-super-delegation
  def update(self, instance, validated_data):
    """Implement ABC."""
    return super().update(instance, validated_data)
