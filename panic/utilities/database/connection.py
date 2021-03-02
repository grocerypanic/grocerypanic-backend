"""Database connection utilities."""

import sys
import time

from django.db import connection
from django.db.utils import OperationalError


def wait_for_database_connection(interval, message=None):
  """Wait until the database is ready to use.

  :param interval: The time in seconds between polls
  :type interval: float
  :param message: An optional message to write to stdout
  :type message: str
  """
  while True:
    try:
      connection.ensure_connection()
      break
    except OperationalError:
      if message:
        sys.stdout.write(message)
      time.sleep(interval)
