"""Test rebuild_item_quantities admin command."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase

from .. import rebuild_item_quantities as module
from ..rebuild_item_quantities import MESSAGE_REBUILDING, MESSAGE_SUCCESS


class TestCommand(TestCase):
  """Test the rebuild_item_quantities command."""

  @classmethod
  def setUpTestData(cls):
    cls.output_stdout = StringIO()
    cls.output_stderr = StringIO()

  def setUp(self):
    self.rebuilder = None

  def tearDown(self):
    pass

  def _call_command(self):
    with patch(
        module.__name__ + '.Item.objects.rebuild_quantities_from_inventory'
    ) as self.rebuilder:
      call_command(
          'rebuild_item_quantities',
          stdout=self.output_stdout,
          stderr=self.output_stderr,
          no_color=True
      )

  @patch(
      module.__name__ + ".AdminConfirmation.are_you_sure", return_value=False
  )
  def test_command_no_confirmation(self, _):
    self._call_command()
    self.rebuilder.assert_not_called()

  @patch(module.__name__ + ".AdminConfirmation.are_you_sure", return_value=True)
  def test_command_calls_rebuild_manager_method_yes(self, _):
    self._call_command()
    self.rebuilder.assert_called_once_with(confirm=True)

  @patch(module.__name__ + ".AdminConfirmation.are_you_sure", return_value=True)
  def test_generates_no_stdout_or_stderr(self, _):
    self._call_command()

    stdout_capture = self.output_stdout.getvalue()

    self.assertIn(
        MESSAGE_REBUILDING,
        stdout_capture,
    )
    self.assertIn(
        MESSAGE_SUCCESS,
        stdout_capture,
    )

    self.assertEqual(self.output_stderr.getvalue(), "")
