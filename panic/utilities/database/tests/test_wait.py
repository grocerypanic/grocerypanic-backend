"""Test the database wait utilities."""

from unittest.mock import patch

from django.db.utils import OperationalError
from django.test import TestCase

from ...tests.fixtures.stdout import capture_stdout
from .. import connection as wait_module
from ..connection import wait_for_database_connection


class TestWaitForDatabaseConnection(TestCase):
  """Test the wait_for_database_connection function."""

  @patch(wait_module.__name__ + ".connection.ensure_connection")
  def test_database_available(self, m_connection):
    m_connection.return_value = True
    wait_for_database_connection(1)
    m_connection.assert_called_once()

  @patch("time.sleep", return_value=True)
  @patch(wait_module.__name__ + ".connection.ensure_connection")
  def test_database_wait(self, m_connection, _):
    message = "waiting"
    with capture_stdout() as stdout:
      m_connection.side_effect = [OperationalError] * 5 + [True]
      wait_for_database_connection(1, message)
      self.assertEqual(m_connection.call_count, 6)

    self.assertEqual(
        stdout.getvalue(),
        message * 5,
    )

  @patch("time.sleep", return_value=True)
  @patch(wait_module.__name__ + ".connection.ensure_connection")
  def test_database_wait_wo_message(self, m_connection, _):
    with capture_stdout() as stdout:
      m_connection.side_effect = [OperationalError] * 5 + [True]
      wait_for_database_connection(1)
      self.assertEqual(m_connection.call_count, 6)

    self.assertEqual(
        stdout.getvalue(),
        "",
    )
