"""AppConfig for the kitchen app."""

from django.apps import AppConfig


class KitchenConfig(AppConfig):
  """AppConfig for the kitchen app."""

  name = 'kitchen'
  default_auto_field = 'django.db.models.BigAutoField'

  def ready(self):
    """Load Signals."""
    # pylint: disable=unused-import, import-outside-toplevel
    from .signals import item, transaction
