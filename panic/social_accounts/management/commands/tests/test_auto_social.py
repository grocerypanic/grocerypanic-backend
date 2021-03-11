"""Test the autosocial management command."""

from io import StringIO
from unittest.mock import patch

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase

from .. import autosocial as command_module
from ..autosocial import SUCCESS_MESSAGE

COMMAND_MODULE = command_module.__name__


@patch(COMMAND_MODULE + ".create_social_app")
class AutoSocialTestCase(SimpleTestCase):
  """Test the autosocial management command."""

  def _call_command(self, provider):
    call_command(
        'autosocial',
        provider,
        stdout=self.output_stdout,
        stderr=self.output_stderr,
        no_color=True
    )

  def _validate_success(self):
    self.assertIn(
        SUCCESS_MESSAGE,
        self.output_stdout.getvalue(),
    )
    self.assertEqual(
        self.output_stderr.getvalue(),
        "",
    )

  def setUp(self):
    self.output_stdout = StringIO()
    self.output_stderr = StringIO()

  def test_autosocial_create_google(self, _):
    self._call_command("google")
    self._validate_success()

  def test_autosocial_create_facebook(self, _):
    self._call_command("facebook")
    self._validate_success()

  def test_autosocial_create_invalid(self, _):
    with self.assertRaises(CommandError):
      self._call_command("invalid")

  def test_autosocial_exception(self, m_create):
    m_create.side_effect = Exception("error")

    with self.assertRaises(CommandError) as raised:
      self._call_command("facebook")

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
