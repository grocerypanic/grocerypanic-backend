"""Test wait_for_db admin command."""

from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from ....toctree import factory as factory_module
from .. import toctree as command_module
from ..toctree import (
    NO_SELECTION_MADE,
    VALIDATION_ERROR,
    VALIDATION_SUCCESS,
    WRITING_SUCCESS,
)

FACTORY_MODULE = factory_module.__name__
COMMAND_MODULE = command_module.__name__


@override_settings(TOCTREE_FACTORY_SETTINGS=None)
class CommandTests(TestCase):
  """Test the wait_for_db admin command."""

  def test_no_selection(self):
    capture = StringIO()
    with self.assertRaises(CommandError) as raised:
      call_command("toctree", stdout=capture)
    self.assertEqual("", capture.getvalue())
    self.assertEqual(raised.exception.args[0], NO_SELECTION_MADE)

  @patch(FACTORY_MODULE + ".TocTreeFactory.build")
  def test_no_errors(self, m_build):
    m_build.return_value.validate.return_value.errors = []
    capture = StringIO()
    call_command("toctree", "--check", stdout=capture)
    m_build.assert_called_once()
    m_build.return_value.validate.assert_called_once()
    self.assertIn(VALIDATION_SUCCESS, capture.getvalue())

  @patch(FACTORY_MODULE + ".TocTreeFactory.build")
  def test_errors(self, m_build):
    error_definitions = ["error1", "error2"]
    m_build.return_value.validate.return_value.errors = error_definitions
    capture = StringIO()
    with self.assertRaises(CommandError) as raised:
      call_command("toctree", "--check", stdout=capture)
    m_build.return_value.validate.assert_called_once()
    m_build.assert_called_once()
    self.assertEqual(raised.exception.args[0], VALIDATION_ERROR)
    for error in error_definitions:
      self.assertIn(error, capture.getvalue())

  @patch(FACTORY_MODULE + ".TocTreeFactory.build")
  def test_diff(self, m_build):
    error_definitions = ["error1", "error2"]
    diff_definitions = {
        "error1": "play more music",
        "error2": "study more korean",
    }

    m_build.return_value.validate.return_value.errors = error_definitions
    m_build.return_value.validate.return_value.diff = diff_definitions
    capture = StringIO()
    with self.assertRaises(CommandError) as raised:
      call_command("toctree", "--check", stdout=capture)
    m_build.return_value.validate.assert_called_once()
    m_build.assert_called_once()
    self.assertEqual(raised.exception.args[0], VALIDATION_ERROR)
    for error in error_definitions:
      self.assertIn(diff_definitions[error], capture.getvalue())

  @patch(FACTORY_MODULE + ".TocTreeFactory.build")
  @patch(COMMAND_MODULE + ".Confirmation.are_you_sure", return_value=False)
  def test_write_unconfirmed(self, _, m_build):
    capture = StringIO()
    call_command("toctree", "--write", stdout=capture)
    m_build.assert_not_called()
    self.assertNotIn(WRITING_SUCCESS, capture.getvalue())

  @patch(FACTORY_MODULE + ".TocTreeFactory.build")
  @patch(COMMAND_MODULE + ".Confirmation.are_you_sure", return_value=True)
  def test_write_confirmed(self, _, m_build):
    capture = StringIO()
    call_command("toctree", "--write", stdout=capture)
    m_build.return_value.write.assert_called_once()
    m_build.assert_called_once()
    self.assertIn(WRITING_SUCCESS, capture.getvalue())
