"""Test the validators used by the Transaction Model."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ...item import MAXIMUM_QUANTITY, MINIMUM_QUANTITY
from ..transaction import (
    TransactionQuantityValidator,
    related_item_quantity_validator,
)


class TestTransactionQuantityValidator(TestCase):
  """Test the TransactionQuantityValidator validator class."""

  def setUp(self):
    self.instance = TransactionQuantityValidator(MAXIMUM_QUANTITY)

  def test_upper_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      self.instance(MAXIMUM_QUANTITY + 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            "This value must be non-zero integer between "
            f"-{MAXIMUM_QUANTITY} and {MAXIMUM_QUANTITY}."
        ],
    )

  def test_lower_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      self.instance((-1 * MAXIMUM_QUANTITY) - 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            "This value must be non-zero integer between "
            f"-{MAXIMUM_QUANTITY} and {MAXIMUM_QUANTITY}."
        ],
    )

  def test_zero(self):
    with self.assertRaises(ValidationError) as raised:
      self.instance(0)

    self.assertListEqual(
        raised.exception.messages,
        [
            "This value must be non-zero integer between "
            f"-{MAXIMUM_QUANTITY} and {MAXIMUM_QUANTITY}."
        ],
    )

  def test_positive(self):
    self.instance(1)


class TestRelatedItemQuantityValidator(TestCase):

  def test_upper_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      related_item_quantity_validator(MAXIMUM_QUANTITY + 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            f"This object's 'quantity' may not reduced below "
            f"{MINIMUM_QUANTITY}, or above {MAXIMUM_QUANTITY}."
        ],
    )

  def test_lower_bounds(self):
    with self.assertRaises(ValidationError) as raised:
      related_item_quantity_validator(MINIMUM_QUANTITY - 1)

    self.assertListEqual(
        raised.exception.messages,
        [
            f"This object's 'quantity' may not reduced below "
            f"{MINIMUM_QUANTITY}, or above {MAXIMUM_QUANTITY}."
        ],
    )

  def test_zero(self):
    related_item_quantity_validator(0)

  def test_positive(self):
    related_item_quantity_validator(1)
