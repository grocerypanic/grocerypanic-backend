"""AppConfig for the social_accounts app."""

from django.apps import AppConfig


class SocialAccountsConfig(AppConfig):
  """AppConfig for the social_accounts app."""

  name = 'social_accounts'

  def ready(self):
    """Load signals."""
    # pylint: disable=unused-import, import-outside-toplevel
    from .signals import presocial_login
