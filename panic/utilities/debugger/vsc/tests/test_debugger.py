"""Test the VSC debugger interface to Django."""

import sys
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from ....tests.fixtures.stdout import capture_stdout
from .. import STARTUP_MESSAGE, Debugger

DEBUGGER_MODULE = Debugger.__module__


class TestDebugger(SimpleTestCase):
  """Test the Debugger class."""

  def setUp(self):
    self.debugger = Debugger()

  @patch(DEBUGGER_MODULE + ".os.getenv", return_value="1")
  def test_has_debug_enabled_true(self, m_getenv):
    self.assertTrue(self.debugger.has_debug_enabled(),)
    m_getenv.assert_called_once_with("DJANGO_REMOTE_DEBUGGING")

  @patch(DEBUGGER_MODULE + ".os.getenv", return_value=None)
  def test_has_debug_enabled_false(self, m_getenv):
    self.assertFalse(self.debugger.has_debug_enabled(),)
    m_getenv.assert_called_once_with("DJANGO_REMOTE_DEBUGGING")

  @patch(DEBUGGER_MODULE + ".os.getenv", return_value="1")
  def test_is_main_process_true(self, m_getenv):
    self.assertTrue(self.debugger.is_main_process(),)
    m_getenv.assert_called_once_with("RUN_MAIN")

  @patch(DEBUGGER_MODULE + ".os.getenv", return_value=None)
  def test_is_main_process_false(self, m_getenv):
    self.assertFalse(self.debugger.is_main_process(),)
    m_getenv.assert_called_once_with("RUN_MAIN")

  @patch.object(sys, 'argv', ['./manage.py', 'runserver', '0.0.0.0:8080'])
  def test_is_run_server_command_true(self):
    self.assertTrue(self.debugger.is_run_server_command(),)

  @patch.object(sys, 'argv', ['./manage.py', 'migrate', 'someapp'])
  def test_is_run_server_command_false(self):
    self.assertFalse(self.debugger.is_run_server_command(),)

  @patch(DEBUGGER_MODULE + ".Debugger.is_run_server_command", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.has_debug_enabled", return_value=False)
  @patch(DEBUGGER_MODULE + ".Debugger._start_debugger")
  def test_debug_not_enable(self, m_start, _has_debug, _is_run):
    self.debugger.debug()
    m_start.assert_not_called()

  @patch(
      DEBUGGER_MODULE + ".Debugger.is_run_server_command", return_value=False
  )
  @patch(DEBUGGER_MODULE + ".Debugger.has_debug_enabled", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger._start_debugger")
  def test_debug_not_server_command(self, m_start, _has_debug, _is_run):
    self.debugger.debug()
    m_start.assert_not_called()

  @patch(DEBUGGER_MODULE + ".Debugger.is_run_server_command", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.has_debug_enabled", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.is_main_process", return_value=False)
  @patch(DEBUGGER_MODULE + ".Debugger._start_debugger")
  def test_debug_not_main_process(self, m_start, _is_main, _has_debug, _is_run):
    self.debugger.debug()
    m_start.assert_not_called()

  @patch(DEBUGGER_MODULE + ".Debugger.is_run_server_command", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.has_debug_enabled", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.is_main_process", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger._start_debugger")
  def test_debug_starts(self, m_start, _is_main, _has_debug, _is_run):
    self.debugger.debug()
    m_start.assert_called_once_with()

  @patch(DEBUGGER_MODULE + ".Debugger.is_run_server_command", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.has_debug_enabled", return_value=True)
  @patch(DEBUGGER_MODULE + ".Debugger.is_main_process", return_value=True)
  @patch(DEBUGGER_MODULE + ".os.getenv", return_value="2323")
  @patch(DEBUGGER_MODULE + ".importlib.import_module")
  def test_debugpy_starts(self, m_lib, _getenv, _is_main, _has_debug, _is_run):
    m_lib.return_value = Mock()

    with capture_stdout() as stdout:
      self.debugger.debug()

    self.assertIn(STARTUP_MESSAGE, stdout.getvalue())

    m_lib.assert_called_once_with("debugpy")
    m_lib.return_value.listen.assert_called_once_with(("0.0.0.0", 2323))
    m_lib.return_value.wait_for_client.assert_called_once()
