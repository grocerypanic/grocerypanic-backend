"""Tests for the TocTree class."""

from unittest import TestCase
from unittest.mock import Mock

from .. import TocTree
from .fixtures.fixtures_toctree import DESTINATION


class TestTocTreeDiscovery(TestCase):
  """Test the TocTree class."""

  def setUp(self):
    self.validator = Mock()
    self.writer = Mock()
    self.tree = TocTree(DESTINATION, self.validator, self.writer)

  def test_root(self):
    self.assertEqual(
        self.tree.root,
        DESTINATION,
    )

  def test_validate(self):
    results = self.tree.validate()

    self.validator.accept.assert_called_once_with(self.tree)
    self.validator.validate.assert_called_once_with()

    self.assertEqual(
        results,
        self.validator,
    )

  def test_writer(self):
    self.tree.write()

    self.writer.accept.assert_called_once_with(self.tree)
    self.writer.write.assert_called_once_with()
