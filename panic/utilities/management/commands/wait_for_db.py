"""A django admin command to wait for the database to be accessible."""

from django.conf import settings
from django.core.management.base import BaseCommand

from ...database.connection import wait_for_database_connection

WAIT_TIME = getattr(settings, 'WAIT_FOR_DB_INTERVAL', 1)
INITIALIZATION_MESSAGE = "Waiting for database..."
SUCCESS_MESSAGE = "Database available!"
WAITING_MESSAGE = f"Database unavailable, waiting {WAIT_TIME} second(s)..."


class Command(BaseCommand):
  """Django command that waits for the database to be available."""

  help = 'Pauses for database connectivity before proceeding.'

  def handle(self, *args, **options):
    """Command implementation."""
    self.stdout.write(INITIALIZATION_MESSAGE)
    wait_for_database_connection(WAIT_TIME, WAITING_MESSAGE)
    self.stdout.write(self.style.SUCCESS(SUCCESS_MESSAGE))
