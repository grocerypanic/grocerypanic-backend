"""Test the abstract validator."""

from unittest import TestCase
from unittest.mock import Mock

from ...tests.fixtures.abc import concretor
from ..bases import AbstractValidator


class AbstractValidatorTest(TestCase):
  """Test the AbstractValidator class."""

  def setUp(self):
    self.mock_logger = Mock()
    self.validator = concretor(AbstractValidator)(self.mock_logger)

  def test_instance(self):
    self.assertEqual(
        self.validator.logger,
        self.mock_logger,
    )

  def test_accept(self):
    self.validator.accept(None)

  def test_validate(self):
    self.validator.validate()
