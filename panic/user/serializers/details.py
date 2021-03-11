"""Detail serializer for the User model."""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .bases import UserBase

UserModel = get_user_model()


class UserDetailsSerializer(
    UserBase,
    serializers.ModelSerializer,
):
  """User details serializer."""

  class Meta:
    model = UserModel
    fields = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'language_code',
        'has_profile_initialized',
        'timezone',
    )
    read_only_fields = (
        'id',
        'email',
    )
