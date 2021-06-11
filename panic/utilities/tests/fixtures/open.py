"""Fixtures for working with files."""

from io import StringIO
from unittest.mock import Mock


class MultiWriteOpenMock:
  """Mock implementation of `open` that supports multiple writes."""

  def __init__(self):
    self.buffer = {}

  def __call__(self, file_name, *args, **kwargs):
    self.buffer[file_name] = StringIO()
    self.buffer[file_name].close = Mock()
    return self.buffer[file_name]
