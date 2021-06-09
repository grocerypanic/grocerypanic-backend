"""Test the Inventory model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_inventory import InventoryTestHarness
from .. import constants
from ..inventory import Inventory


class TestItem(ModelTestMixin, InventoryTestHarness):
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

    self.assertQuerysetEqual(query, [created])

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


class TestInventoryRelatedFields(InventoryTestHarness):
  """Test the Inventory model's related fields."""

  @classmethod
  def create_data_hook(cls):
    cls.data = {
        'item': cls.item1,
        'remaining': cls.initial_quantity,
        'transaction': cls.transaction1,
    }

  def setUp(self):
    super().setUp()
    dependency_kwargs = {
        'datetime_object': self.today,
        'quantity': self.initial_quantity
    }
    test_data = self.create_dependencies(2, **dependency_kwargs)
    self.item2 = test_data['item']
    self.transaction2 = test_data['transaction']

  def test_wrong_item(self):
    wrong_related_item = dict(self.data)
    wrong_related_item.update({'item': self.item2})

    with self.assertRaises(ValidationError) as raised:
      self.create_test_instance(**wrong_related_item)

    self.assertDictEqual(
        raised.exception.message_dict, {
            'item': ["This must match the 'transaction' field."],
            'transaction': ["This field must match the 'item' field."],
        }
    )

  def test_wrong_transaction(self):
    wrong_related_item = dict(self.data)
    wrong_related_item.update({'transaction': self.transaction2})

    with self.assertRaises(ValidationError) as raised:
      self.create_test_instance(**wrong_related_item)

    self.assertDictEqual(
        raised.exception.message_dict, {
            'item': ["This must match the 'transaction' field."],
            'transaction': ["This field must match the 'item' field."],
        }
    )
