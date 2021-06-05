"""AppConfig for the user app."""

from django.apps import AppConfig


class UserConfig(AppConfig):
  """AppConfig for the user app."""

  name = 'user'
  default_auto_field = 'django.db.models.BigAutoField'

  def ready(self):
    """Load Signals."""
    # pylint: disable=unused-import, import-outside-toplevel
    from .signals import signup
