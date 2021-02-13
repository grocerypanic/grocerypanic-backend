"""Custom user model."""

import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models
from timezone_field import TimeZoneField

from .validators.user import validate_language

CUSTOM_USER_MODEL_FIELDS = (
    'language_code',
    'has_profile_initialized',
    'timezone',
)


class User(AbstractUser):
  """Custom user model."""

  DEFAULT_TIMEZONE = pytz.utc.zone
  DEFAULT_LANGUAGE_CODE = 'en'

  language_code = models.CharField(
      max_length=20,
      default=DEFAULT_LANGUAGE_CODE,
      validators=[validate_language],
  )
  has_profile_initialized = models.BooleanField(default=False)
  timezone = TimeZoneField(default=DEFAULT_TIMEZONE)

  class Meta:
    db_table = 'auth_user'

  # pylint: disable=W0222
  def save(self, *args, **kwargs):
    """Clean and save model."""
    self.full_clean()
    return super(User, self).save(*args, **kwargs)
