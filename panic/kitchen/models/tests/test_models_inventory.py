"""Test the Inventory model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixtures_inventory import InventoryTestHarness
from .. import constants
from ..inventory import Inventory
from .fixtures.fixture_models import generate_base


class TestItem(generate_base(InventoryTestHarness)):
  """Test the Inventory model."""

  @classmethod
  def create_data_hook(cls):
    cls.fields = {}
    cls.data = {
        'item': cls.item1,
        'remaining': cls.initial_quantity,
        'transaction': cls.transaction1,
    }

  def setUp(self):
    Inventory.objects.all().delete()
    super().setUp()

  def test_create(self):
    created = self.create_test_instance(**self.data)
    query = Inventory.objects.filter(item=self.item1)

    self.assertQuerysetEqual(query, map(repr, [created]))

  def test_str(self):
    inventory = self.create_test_instance(**self.data)
    expected = (
        f"{inventory.remaining} units of {self.item1.name}, "
        f"purchased at {self.transaction1.datetime}"
    )

    self.assertEqual(expected, str(inventory))

  def test_negative_remaining(self):
    inventory = self.create_test_instance(**self.data)
    inventory.remaining = constants.MINIMUM_QUANTITY - 1
    with self.assertRaises(ValidationError):
      inventory.save()

  def test_positive_remaining(self):
    inventory = self.create_test_instance(**self.data)
    inventory.remaining = constants.MAXIMUM_QUANTITY + 1
    with self.assertRaises(ValidationError):
      inventory.save()
