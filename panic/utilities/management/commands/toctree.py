"""A django admin command to manage the Sphinx TOC tree."""

from django.core.management.base import BaseCommand, CommandError

from ...filesystem.paths import (
    DOCUMENTATION_CODEBASE_DIRECTORY,
    PROJECT_ROOT_DIRECTORY,
)
from ...toctree.factory import TocTreeFactory
from ...toctree.settings import load_settings
from ..shared.confirmation import ManagementConfirmation

VALIDATION_ERROR = "TOC tree is not up to date."
VALIDATION_SUCCESS = "TOC tree up to date."
WRITING_SUCCESS = "TOC tree written to disk"
NO_SELECTION_MADE = "You must specify '--check' or '--write'."


class Confirmation(ManagementConfirmation):
  """Confirmation dialogue."""

  confirm_message = (
      "This command will erase and rebuild the existing TOC tree.\n"
      "Are you absolutely sure you wish to proceed [Y/n] ? "
  )
  confirm_yes = "Y"


class Command(BaseCommand):
  """Django management command to manage the Sphinx TOC tree.

  - Validate an existing Sphinx TOC tree's contents::

    ./manage.py toctree --check

  - Write a calculated TOC tree to disk (erasing any existing content)::

    ./manage.py toctree --write
  """

  help = 'Manage the Sphinx TOC tree during development.'

  def add_arguments(self, parser):
    """Add argument to the parser."""
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-c',
        '--check',
        action='store_true',
        help='Check the TOC tree contents',
    )
    group.add_argument(
        '-w',
        '--write',
        action='store_true',
        help='Write the TOC tree to disk',
    )

  def handle(self, *args, **options):
    """Command implementation."""
    check = options['check']
    write = options['write']

    if check or write:
      method = self.__check if check else self.__write
      factory = TocTreeFactory(
          str(PROJECT_ROOT_DIRECTORY),
          str(DOCUMENTATION_CODEBASE_DIRECTORY),
          load_settings(),
      )
      method(factory)
    else:
      raise CommandError(NO_SELECTION_MADE)

  def __check(self, factory):
    tree = factory.build()
    results = tree.validate()

    if results.errors:
      for error in results.errors:
        self.stdout.write(self.style.ERROR(error))
        if error in results.diff:
          self.stdout.write(results.diff[error])
      raise CommandError(VALIDATION_ERROR)

    self.stdout.write(self.style.SUCCESS(VALIDATION_SUCCESS))

  def __write(self, factory):
    confirm = Confirmation()

    if confirm.are_you_sure():
      tree = factory.build()
      tree.write()
      self.stdout.write(self.style.SUCCESS(WRITING_SUCCESS))
