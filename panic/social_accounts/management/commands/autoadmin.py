"""A Django management command to create an admin superuser."""

from django.core.management.base import BaseCommand, CommandError

from utilities.models.generators.superuser import create_superuser

SUCCESS_MESSAGE = 'Successfully created admin user.'


class Command(BaseCommand):
  """Creates an admin superuser with a set of credentials.

  - Generate Admin Account::

    ./manage.py autoadmin

  - Credentials:
    Username: admin
    Password: admin
  """

  help = 'Adds a admin user without user interaction.'

  def handle(self, *args, **options):
    """Command implementation."""
    try:
      create_superuser()
    except Exception as raised:
      raise CommandError(*raised.args) from raised

    self.stdout.write(self.style.SUCCESS(SUCCESS_MESSAGE))
