"""AppConfig for the kitchen app."""

from django.apps import AppConfig


class KitchenConfig(AppConfig):
  """AppConfig for the kitchen app."""

  name = 'kitchen'

  def ready(self):
    """Load Signals."""
    # pylint: disable=unused-import, import-outside-toplevel
    from .signals import transaction, item
