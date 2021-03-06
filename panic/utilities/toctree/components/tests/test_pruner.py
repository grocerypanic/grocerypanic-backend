"""Tests for the TocTreePruner class."""

from unittest import TestCase
from unittest.mock import Mock

from ... import TocTree
from ...settings import TocTreeFactorySettings
from ...tests.fixtures.fixtures_toctree import (
    DESTINATION,
    DESTINATION_FILE_SYSTEM,
    MODULE_MAPPINGS,
    SOURCE,
    SOURCE_FILE_SYSTEM,
)
from ..pruner import TocTreePruner


class Settings(TocTreeFactorySettings):
  """Configured TocTreeFactorySettings for test."""

  files_filter_list = [f"{SOURCE}/folder1/manage.py"]


class TocTreePrunerTest(TestCase):
  """Test the TocTreePruner class."""

  def setUp(self):
    self.tree = TocTree(DESTINATION, Mock(), Mock())
    self.pruner = TocTreePruner(SOURCE)
    self.tree.source_structure = SOURCE_FILE_SYSTEM

  def test_pruned_file_system(self):
    self.pruner.accept(self.tree)
    self.pruner.prune(Settings())

    self.assertEqual(
        self.pruner.pruned_file_system,
        DESTINATION_FILE_SYSTEM,
    )

  def test_pruned_modules(self):
    self.pruner.accept(self.tree)
    self.pruner.prune(Settings())

    self.assertEqual(
        self.pruner.pruned_module_names,
        MODULE_MAPPINGS,
    )
