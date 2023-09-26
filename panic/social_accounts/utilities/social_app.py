"""Generate allauth social apps."""

import os

from allauth.socialaccount.models import SocialApp
from django.core.exceptions import ImproperlyConfigured

ENVIRONMENT_VARIABLE_ERROR = "Environment variables not set correctly."
ALREADY_EXISTS_ERROR = "Social app already exists."


def create_social_app(provider, site_number=1):
  """Create an allauth SocialApp model object for the provider specified.

  You need to have two Environment Variables set with the following details::
    - %PROVIDERNAME%_ID          : the non sensitive identifier of the provider
    - %PROVIDERNAME%_SECRET_KEY  : the provider's secret identifier

  :param provider: The provider name as a string
  :type provider: str
  :param site_number: The site number to create this SocialApp for
  :type site_number: int

  :returns: The created SocialApp instance
  :rtype: :class:`allauth.socialaccount.models.SocialApp`
  :raises: :class:`django.core.management.base.CommandError`
  """

  client_id = os.getenv(('%s_ID' % provider).upper(), None)
  secret = os.getenv(('%s_SECRET_KEY' % provider).upper(), None)

  if client_id is None or secret is None:
    raise ImproperlyConfigured(ENVIRONMENT_VARIABLE_ERROR)

  query = SocialApp.objects.all().filter(provider=provider).count()
  if query > 0:
    raise ImproperlyConfigured(ALREADY_EXISTS_ERROR)

  social_app = SocialApp(
      provider=provider,
      name='%s oauth login' % provider,
      client_id=client_id,
      secret=secret
  )

  social_app.save()
  social_app.sites.add(site_number)

  return social_app
