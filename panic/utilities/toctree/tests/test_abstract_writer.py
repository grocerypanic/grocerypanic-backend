"""Test the abstract writer."""

from unittest import TestCase
from unittest.mock import Mock

from ...tests.fixtures.abc import concretor
from ..bases import AbstractWriter


class AbstractValidatorTest(TestCase):
  """Test the AbstractWriter class."""

  def setUp(self):
    self.mock_logger = Mock()
    self.writer = concretor(AbstractWriter)(self.mock_logger)

  def test_instance(self):
    self.assertEqual(
        self.writer.logger,
        self.mock_logger,
    )

  def test_accept(self):
    self.writer.accept(None)

  def test_write(self):
    self.writer.write()
