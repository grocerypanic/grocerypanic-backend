"""Test the validators used by the Transaction Model."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ... import constants
from ..transaction import (
    TransactionQuantityValidator,
    related_item_quantity_validator,
)


class TestTransactionQuantityValidator(TestCase):
  """Test the TransactionQuantityValidator validator class."""

  def setUp(self):
    self.instance = TransactionQuantityValidator(constants.MAXIMUM_QUANTITY)

  def test_upper_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      self.instance(constants.MAXIMUM_QUANTITY + 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            "This value must be non-zero integer between "
            f"-{constants.MAXIMUM_QUANTITY} and {constants.MAXIMUM_QUANTITY}."
        ],
    )

  def test_lower_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      self.instance((-1 * constants.MAXIMUM_QUANTITY) - 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            "This value must be non-zero integer between "
            f"-{constants.MAXIMUM_QUANTITY} and {constants.MAXIMUM_QUANTITY}."
        ],
    )

  def test_zero(self):
    with self.assertRaises(ValidationError) as raised:
      self.instance(0)

    self.assertListEqual(
        raised.exception.messages,
        [
            "This value must be non-zero integer between "
            f"-{constants.MAXIMUM_QUANTITY} and {constants.MAXIMUM_QUANTITY}."
        ],
    )

  def test_positive(self):
    self.instance(1)


class TestRelatedItemQuantityValidator(TestCase):
  """Test the related_item_quantity_validator function."""

  def test_upper_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      related_item_quantity_validator(constants.MAXIMUM_QUANTITY + 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            f"This object's 'quantity' may not reduced below "
            f"{constants.MINIMUM_QUANTITY}, or above "
            f"{constants.MAXIMUM_QUANTITY}."
        ],
    )

  def test_lower_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      related_item_quantity_validator(constants.MINIMUM_QUANTITY - 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            f"This object's 'quantity' may not reduced below "
            f"{constants.MINIMUM_QUANTITY}, or above "
            f"{constants.MAXIMUM_QUANTITY}."
        ],
    )

  def test_zero(self):
    related_item_quantity_validator(0)

  def test_positive(self):
    related_item_quantity_validator(1)
