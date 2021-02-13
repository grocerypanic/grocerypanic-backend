"""Kitchen base view classes."""

from spa_security.mixins import CSRFMixin


class KitchenBaseView(
    CSRFMixin,
):
  """Kitchen base view."""
