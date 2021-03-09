"""A management command to create test data."""

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from ...tests.fixtures.bulk_testdata import BulkTestDataGenerator

ERROR_MESSAGE = 'The specified user does not exist.'
SUCCESS_MESSAGE = 'Test data created.'


class Command(BaseCommand):
  """Management command that loads test data into the database."""

  help = 'Loads sets of pre-defined test data into the database'

  def add_arguments(self, parser):
    """Entry point for subclassed commands to add custom arguments."""
    parser.add_argument(
        'user',
        nargs=1,
        type=str,
    )

  def handle(self, *args, **options):
    """Command implementation."""
    username = options['user'][0]

    try:
      generator = BulkTestDataGenerator(username)
    except ObjectDoesNotExist:
      self.stderr.write(self.style.ERROR(ERROR_MESSAGE))
      return

    generator.generate_data()
    self.stdout.write(self.style.SUCCESS(SUCCESS_MESSAGE))
