"""Social_accounts app AppConfig."""

from django.apps import AppConfig


class SocialAccountsConfig(AppConfig):
  """Social_accounts app AppConfig."""

  name = 'social_accounts'

  def ready(self):
    """Load signals."""
    # pylint: disable=W0611,C0415
    from .signals import presocial_login
