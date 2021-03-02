"""A django admin command to wait for the database to be accessible."""

from django.core.management.base import BaseCommand

from utilities.database.connection import wait_for_database_connection

INITIALIZATION_MESSAGE = "Waiting for database..."
SUCCESS_MESSAGE = "Database available!"
WAITING_MESSAGE = "Database unavailable, waiting 1 second..."


class Command(BaseCommand):
  """Django command that waits for the database to be available."""

  help = 'Pauses for database connectivity before proceeding.'

  def handle(self, *args, **options):
    """Command implementation."""
    self.stdout.write(INITIALIZATION_MESSAGE)
    wait_for_database_connection(1, WAITING_MESSAGE)
    self.stdout.write(self.style.SUCCESS(SUCCESS_MESSAGE))
