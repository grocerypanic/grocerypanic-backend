"""A django admin command to create test data."""

from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from .utils.generate_testdata import DataGenerator


class Command(BaseCommand):
  """Django command that loads test data into the database."""

  help = 'Loads sets of pre-defined test data into the database'

  def add_arguments(self, parser):
    """Entry point for subclassed commands to add custom arguments."""
    parser.add_argument(
        'user',
        nargs=1,
        type=str,
    )

  def __get_user(self, username):
    try:
      return get_user_model().objects.get(username=username)
    except ObjectDoesNotExist:
      return None

  def handle(self, *args, **options):
    """Command implementation."""
    username = options['user'][0]
    user = self.__get_user(username)
    if user:
      generator = DataGenerator(user)
      generator.generate_data()
    else:
      self.stderr.write(self.style.ERROR('The specified user does not exist.'))
