"""A Django management command to add a social login provider."""

from django.core.management.base import BaseCommand, CommandError

from ...utilities.social_app import create_social_app

SUCCESS_MESSAGE = 'Successfully created social login provider.'


class Command(BaseCommand):
  """Adds a social login provider configured via environment variables.

  - Generate Social Login Provider::

    ./manage.py autosocial [PROVIDER]

  - Credentials::

    - client_id ENV_VAR -> %PROVIDER%_ID
    - secret    ENV_VAR -> %PROVIDER%_SECRET_KEY

  - Supported Providers::

    - google
    - facebook
  """

  help = 'Adds a social login provider without user interaction.'

  def add_arguments(self, parser):
    """Add arguments to the parser."""
    parser.add_argument(
        'provider', nargs=1, type=str, choices=['google', 'facebook']
    )

  def handle(self, *args, **options):
    """Command implementation."""
    provider = options['provider'][0]

    try:
      create_social_app(provider)
    except Exception as raised:
      raise CommandError(*raised.args) from raised

    self.stdout.write(self.style.SUCCESS(SUCCESS_MESSAGE))
