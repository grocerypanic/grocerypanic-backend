"""Django Automated Social App Creation."""
import os

from allauth.socialaccount.models import SocialApp
from django.core.management.base import BaseCommand


class Command(BaseCommand):
  """Bootstraps Social Authentication by populating social logins based on
  environment variables.

  - Generate Social Login Authorization::

    ./manage.py autosocial [PROVIDER]

  - Credentials::

    - client_id ENV_VAR -> %PROVIDER%_ID
    - secret    ENV_VAR -> %PROVIDER%_SECRET_KEY

  - Supported Providers::

    - google
    - facebook
 """
  help = 'Adds social app configuration without user interaction.'

  def add_arguments(self, parser):
    parser.add_argument(
        'provider', nargs=1, type=str, choices=['google', 'facebook']
    )

  def handle(self, *args, **options):
    provider = options['provider'][0]

    client_id = os.getenv(('%s_ID' % provider).upper(), None)
    secret = os.getenv(('%s_SECRET_KEY' % provider).upper(), None)

    if client_id is None or secret is None:
      self.stderr.write(self.style.ERROR('The required env vars are not set.'))
      return

    query = SocialApp.objects.all().filter(provider=provider).count()
    if query > 0:
      self.stderr.write(self.style.ERROR('The social app already exists.'))
      return

    social_app = SocialApp(
        provider=provider,
        name='%s oauth login' % provider,
        client_id=client_id,
        secret=secret
    )

    social_app.save()
    social_app.sites.add(1)

    self.stdout.write(
        self.style.SUCCESS('Successfully created social app account.')
    )
