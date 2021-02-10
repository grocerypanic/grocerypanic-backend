"""Kitchen View Base Classes"""

from spa_security.mixins import CSRFMixin


class KitchenBaseView(
    CSRFMixin,
):
  """Kitchen App Base View"""
