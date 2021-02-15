"""Custom user app AppConfig."""

from django.apps import AppConfig


class UserConfig(AppConfig):
  """Custom user app AppConfig."""

  name = 'user'

  def ready(self):
    """Load Signals."""
    # pylint: disable=unused-import, import-outside-toplevel
    from .signals import signup
