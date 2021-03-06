"""Fixtures related to stdout."""

import sys
from contextlib import contextmanager
from io import StringIO


@contextmanager
def capture_stdout():
  """Capture stdout from within a context manager."""

  out, sys.stdout = sys.stdout, StringIO()
  try:
    yield sys.stdout
  finally:
    sys.stdout = out
