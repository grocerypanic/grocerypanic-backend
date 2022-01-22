"""Fixtures related to stdout."""

import sys
from contextlib import contextmanager
from io import StringIO
from typing import Generator


@contextmanager
def capture_stdout() -> Generator[StringIO, None, None]:
  """Capture stdout from within a context manager."""

  out, sys.stdout = sys.stdout, StringIO()
  try:
    yield sys.stdout
  finally:
    sys.stdout = out
