"""Test the abstract pruner."""

from unittest import TestCase

from ...tests.fixtures.abc import concretor
from ..bases import AbstractPruner


class AbstractPrunerTest(TestCase):
  """Test the AbstractPruner class."""

  def setUp(self):
    self.mock_source = "source folder"
    self.pruner = concretor(AbstractPruner)(self.mock_source)

  def test_instance(self):
    self.assertEqual(
        self.pruner.source_folder,
        self.mock_source,
    )

  def test_accept(self):
    self.pruner.accept(None)

  def test_write(self):
    self.pruner.prune(None)
