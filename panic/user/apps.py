"""User App AppConfig"""

from django.apps import AppConfig


class UserConfig(AppConfig):
  """User App Configuration"""
  name = 'user'

  def ready(self):
    # pylint: disable=W0611,C0415
    from .signals import signup
