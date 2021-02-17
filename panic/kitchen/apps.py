"""Kitchen app AppConfig."""

from django.apps import AppConfig


class KitchenConfig(AppConfig):
  """Kitchen app AppConfig."""

  name = 'kitchen'

  def ready(self):
    """Load Signals."""
    # pylint: disable=unused-import, import-outside-toplevel
    from .signals import transaction
