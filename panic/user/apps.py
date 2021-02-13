"""Custom user app AppConfig."""

from django.apps import AppConfig


class UserConfig(AppConfig):
  """Custom user app AppConfig."""

  name = 'user'

  def ready(self):
    """Load Signals."""
    # pylint: disable=W0611,C0415
    from .signals import signup
