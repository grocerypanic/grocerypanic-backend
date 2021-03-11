"""Test the autoadmin management command."""

from io import StringIO
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase

from .. import autoadmin as command_module
from ..autoadmin import SUCCESS_MESSAGE

COMMAND_MODULE = command_module.__name__


@patch(COMMAND_MODULE + ".create_superuser")
class AutoAdminTestCase(SimpleTestCase):
  """Test the autoadmin management command."""

  def setUp(self):
    self.output_stdout = StringIO()
    self.output_stderr = StringIO()

  def test_autoadmin_create(self, _):
    call_command(
        'autoadmin',
        stdout=self.output_stdout,
        stderr=self.output_stderr,
        no_color=True
    )

    self.assertIn(
        SUCCESS_MESSAGE,
        self.output_stdout.getvalue(),
    )
    self.assertEqual(
        self.output_stderr.getvalue(),
        "",
    )

  def test_autoadmin_exception(self, m_create):
    m_create.side_effect = Exception("error")

    with self.assertRaises(CommandError) as raised:
      call_command(
          'autoadmin',
          stdout=self.output_stdout,
          stderr=self.output_stderr,
          no_color=True
      )

    self.assertEqual(
        raised.exception.args[0],
        "error",
    )
    self.assertEqual(
        self.output_stdout.getvalue(),
        "",
    )
    self.assertEqual(
        self.output_stderr.getvalue(),
        "",
    )
