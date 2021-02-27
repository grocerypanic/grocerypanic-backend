"""Test rebuild_inventory admin command."""

from io import StringIO
from unittest.mock import Mock, patch

from django.core.management import call_command
from django.test import TestCase

from .. import rebuild_inventory as module
from ..rebuild_inventory import (
    MESSAGE_REBUILDING,
    MESSAGE_SUCCESS,
    MESSAGE_WIPING,
)


class TestCommand(TestCase):
  """Test the rebuild_inventory command."""

  @classmethod
  def setUpTestData(cls):
    cls.output_stdout = StringIO()
    cls.output_stderr = StringIO()

  def setUp(self):
    self.mock_query_set = Mock()
    self.rebuilder = None
    self.inventory = None

  def _call_command(self):
    with patch(
        module.__name__ + '.Transaction.objects.rebuild_inventory_table'
    ) as self.rebuilder:
      with patch(module.__name__ + '.Inventory.objects.all') as self.inventory:
        self.inventory.return_value = self.mock_query_set

        call_command(
            'rebuild_inventory',
            stdout=self.output_stdout,
            stderr=self.output_stderr,
            no_color=True
        )

  def tearDown(self):
    pass

  @patch(
      module.__name__ + ".AdminConfirmation.are_you_sure", return_value=False
  )
  def test_command_no_confirmation(self, _):
    self._call_command()
    self.mock_query_set.delete.assert_not_called()
    self.rebuilder.assert_not_called()

  @patch(module.__name__ + ".AdminConfirmation.are_you_sure", return_value=True)
  def test_command_deletes_all_inventory(self, _):
    self._call_command()
    self.mock_query_set.delete.assert_called_once_with()

  @patch(module.__name__ + ".AdminConfirmation.are_you_sure", return_value=True)
  def test_command_calls_the_rebuild_manager_method(self, _):
    self._call_command()
    self.rebuilder.assert_called_once_with(confirm=True)

  @patch(module.__name__ + ".AdminConfirmation.are_you_sure", return_value=True)
  def test_generates_no_stdout_or_stderr(self, _):
    self._call_command()
    stdout_capture = self.output_stdout.getvalue()

    self.assertIn(
        MESSAGE_WIPING,
        stdout_capture,
    )
    self.assertIn(
        MESSAGE_REBUILDING,
        stdout_capture,
    )
    self.assertIn(
        MESSAGE_SUCCESS,
        stdout_capture,
    )

    self.assertEqual(self.output_stderr.getvalue(), "")
