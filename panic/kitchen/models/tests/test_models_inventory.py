"""Test the Inventory Model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.inventory import InventoryTestHarness
from ..inventory import Inventory
from ..item import MAXIMUM_QUANTITY, MINIMUM_QUANTITY


class TestItem(InventoryTestHarness):

  @classmethod
  def create_data_hook(cls):
    cls.data = {
        'item': cls.item1,
        'remaining': cls.initial_quantity,
        'transaction': cls.transaction1,
    }

  def setUp(self):
    Inventory.objects.all().delete()
    super().setUp()

  def testAddItem(self):
    created = self.create_test_instance(**self.data)
    query = Inventory.objects.filter(item=self.item1)

    self.assertQuerysetEqual(query, map(repr, [created]))

  def testStr(self):
    inventory = self.create_test_instance(**self.data)
    expected = (
        f"{inventory.remaining} units of {self.item1.name}, "
        f"purchased at {self.transaction1.datetime}"
    )

    self.assertEqual(expected, str(inventory))

  def testNegativeRemaining(self):
    inventory = self.create_test_instance(**self.data)
    inventory.remaining = MINIMUM_QUANTITY - 1
    with self.assertRaises(ValidationError):
      inventory.save()

  def testPositiveRemainingOverLimit(self):
    inventory = self.create_test_instance(**self.data)
    inventory.remaining = MAXIMUM_QUANTITY + 1
    with self.assertRaises(ValidationError):
      inventory.save()
