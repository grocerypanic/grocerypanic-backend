"""Fixtures for working with files."""

from io import StringIO
from typing import Any, Dict
from unittest.mock import Mock


class MultiWriteOpenMock:
  """Mock implementation of `open` that supports multiple writes."""

  def __init__(self) -> None:
    self.buffer: Dict[str, StringIO] = {}

  def __call__(self, file_name: str, *args: Any, **kwargs: Any) -> StringIO:
    self.buffer[file_name] = StringIO()
    setattr(self.buffer[file_name], "close", Mock())
    return self.buffer[file_name]
