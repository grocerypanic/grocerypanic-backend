"""Tests for the TocTree Content class."""

from unittest import TestCase
from unittest.mock import Mock

from ... import TocTree
from ...tests.fixtures.fixtures_toctree import (
    DESTINATION,
    DESTINATION_FILE_CONTENT,
    DESTINATION_FILE_SYSTEM,
    MODULE_MAPPINGS,
    SOURCE_FILE_SYSTEM,
)
from ..content import TocTreeContent
from ..logging import logger


class TestTocTreeContent(TestCase):
  """Test the TocTreeContent class."""

  def setUp(self):
    self.tree = TocTree(DESTINATION, Mock(), Mock())
    self.content = TocTreeContent(logger)
    self.tree.source_structure = SOURCE_FILE_SYSTEM
    self.tree.destination_structure = DESTINATION_FILE_SYSTEM
    self.tree.module_names = MODULE_MAPPINGS

  def test_generate(self):
    self.content.accept(self.tree)
    return_value = self.content.generate()

    for name, content in return_value.items():
      self.assertEqual(DESTINATION_FILE_CONTENT[name], content)

    self.assertDictEqual(
        DESTINATION_FILE_CONTENT,
        return_value,
    )
