"""Social Accounts App AppConfig"""

from django.apps import AppConfig


class SocialAccountsConfig(AppConfig):
  """Social Accounts App Configuration"""
  name = 'social_accounts'

  def ready(self):
    # pylint: disable=W0611,C0415
    from .signals import presocial_login
