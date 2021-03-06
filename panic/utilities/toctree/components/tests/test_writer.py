"""Test the TocTreeWriter class."""

from unittest import TestCase
from unittest.mock import Mock, patch

from ....tests.fixtures.open import MultiWriteOpenMock
from ... import TocTree
from ...tests.fixtures.fixtures_toctree import (
    DESTINATION,
    DESTINATION_FILE_CONTENT,
    DESTINATION_FILE_SYSTEM,
)
from .. import writer as writer_module
from ..logging import logger
from ..writer import TocTreeWriter

WRITER_MODULE = writer_module.__name__
MOCK_OPEN = MultiWriteOpenMock()


@patch(WRITER_MODULE + ".open", new=MOCK_OPEN)
@patch(WRITER_MODULE + ".shutil.rmtree")
@patch(WRITER_MODULE + ".os.makedirs")
class TestTocTreeValidation(TestCase):
  """Test the TocTreeValidator class."""

  def setUp(self):
    self.validator = Mock()
    self.writer = TocTreeWriter(logger)
    self.tree = TocTree(DESTINATION, self.validator, self.writer)
    self.tree.content = DESTINATION_FILE_CONTENT
    self.tree.destination_structure = DESTINATION_FILE_SYSTEM

  def test_write_erases_tree(self, _, m_rmtree):
    self.writer.accept(self.tree)
    self.writer.write()
    m_rmtree.assert_called_once_with(DESTINATION)

  def test_write_creates_directories(self, m_makedirs, _):
    self.writer.accept(self.tree)
    self.writer.write()

    for folder_struct in DESTINATION_FILE_SYSTEM:
      folder, _, _ = folder_struct
      m_makedirs.assert_any_call(folder, exist_ok=True)

    self.assertEqual(
        len(DESTINATION_FILE_SYSTEM),
        m_makedirs.call_count,
    )

  def test_write_creates_files(self, _, _unused):
    self.writer.accept(self.tree)
    self.writer.write()

    for file_name, content in DESTINATION_FILE_CONTENT.items():
      self.assertEqual(
          MOCK_OPEN.buffer[file_name].getvalue(),
          "\n".join(content),
      )
