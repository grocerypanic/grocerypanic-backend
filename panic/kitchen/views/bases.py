"""Kitchen base view classes."""

from spa_security.mixins.csrf import CSRFMixin


class KitchenBaseView(
    CSRFMixin,
):
  """Kitchen base view."""
