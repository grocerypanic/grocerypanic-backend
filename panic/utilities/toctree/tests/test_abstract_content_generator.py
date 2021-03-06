"""Test the abstract writer."""

from unittest import TestCase
from unittest.mock import Mock

from ...tests.fixtures.abc import concretor
from ..bases import AbstractContentGenerator


class AbstractContentGeneratorTest(TestCase):
  """Test the AbstractContentGenerator class."""

  def setUp(self):
    self.mock_logger = Mock()
    self.generator = concretor(AbstractContentGenerator)(self.mock_logger)

  def test_instance(self):
    self.assertEqual(
        self.generator.logger,
        self.mock_logger,
    )

  def test_accept(self):
    self.generator.accept(None)

  def test_generate(self):
    self.generator.generate()
