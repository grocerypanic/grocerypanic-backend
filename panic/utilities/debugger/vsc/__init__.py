"""An interface to the VSC remote debugger."""

import importlib
import os
import sys

STARTUP_MESSAGE = "Waiting for debugger client..."


class Debugger:
  """An interface to the VSC remote debugger."""

  def debug(self):
    """Starts the remote debugger, if configured."""
    if not self.has_debug_enabled() or not self.is_run_server_command():
      return
    if self.is_main_process():
      self._start_debugger()

  def has_debug_enabled(self):
    """Determines if remote debugging is enabled.

    :returns: A boolean indicating if remote debugging is enabled.
    :rtype: bool.
    """
    return os.getenv("DJANGO_REMOTE_DEBUGGING") == "1"

  def is_main_process(self):
    """Determines if the main Django process is running.

    :returns: A boolean indicating if the main Django process is running.
    :rtype: bool.
    """
    if os.getenv("RUN_MAIN"):
      return True
    return False

  def is_run_server_command(self):
    """Determines if the `runserver` command was used to start the process.

    :returns: A boolean indicating if the `runserver` command was used.
    :rtype: bool.
    """
    return sys.argv[1] == "runserver"

  def _start_debugger(self):
    debugger = importlib.import_module('debugpy')
    debugger_port = int(os.getenv("DJANGO_DEBUGGER_PORT", "5678"))
    debugger.listen((
        "0.0.0.0",
        debugger_port,
    ))
    print(STARTUP_MESSAGE)
    debugger.wait_for_client()
