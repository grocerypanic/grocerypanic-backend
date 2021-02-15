"""Test wait_for_db admin command."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
  """Test the wait_for_db admin command."""

  def test_wait_for_db_ready(self):
    capture = StringIO()

    with patch("django.db.connection.ensure_connection") as connection:
      connection.return_value = True
      call_command("wait_for_db", stdout=capture)
      self.assertEqual(connection.call_count, 1)

  @patch("time.sleep", return_value=True)
  def test_wait_for_db(self, _):
    capture = StringIO()

    with patch("django.db.connection.ensure_connection") as connection:
      connection.side_effect = [OperationalError] * 5 + [True]
      call_command("wait_for_db", stdout=capture)
      self.assertEqual(connection.call_count, 6)
