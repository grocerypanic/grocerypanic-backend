"""Test the Item model."""

from unittest.mock import patch

from django.core.exceptions import ValidationError
from django.utils import timezone
from freezegun import freeze_time

from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_item import ItemTestHarness
from .. import constants
from .. import item as item_module
from ..item import Item


class TestItem(ModelTestMixin, ItemTestHarness):
  """Test the Item model."""

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.fields = {"name": 255}
    cls.data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3,
    }

  def test_create(self):
    created = self.create_test_instance(**self.data)
    query = Item.objects.filter(name=self.data['name'])

    self.assertQuerysetEqual(query, map(repr, [created]))
    self.assertEqual(query[0].index, self.data['name'].lower())

  def test_unique(self):
    _ = self.create_test_instance(**self.data)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(**self.data)

    count = Item.objects.filter(name=self.data['name']).count()
    assert count == 1

  def test_bleach(self):
    injection_attack = dict(self.data)
    injection_attack['name'] = "Canned Beans<script>alert('hi');</script>"
    sanitized_name = "Canned Beans&lt;script&gt;alert('hi');&lt;/script&gt;"

    _ = self.create_test_instance(**injection_attack)

    query = Item.objects.filter(name=injection_attack['name']).count()
    assert query == 0

    query = Item.objects.filter(name=sanitized_name)
    assert len(query) == 1

    item = query[0]
    self.assertEqual(item.index, sanitized_name.lower())
    self.assertEqual(item.name, sanitized_name)
    self.assertEqual(item.shelf_life, self.data['shelf_life'])
    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.shelf.id, self.shelf1.id)
    self.assertEqual(item.price, self.data['price'])
    self.assertEqual(item.quantity, self.data['quantity'])

  def test_str(self):
    item = self.create_test_instance(**self.data)
    self.assertEqual(self.data['name'], str(item))

  def test_negative_qty(self):
    item = self.create_test_instance(**self.data)
    item.quantity = constants.MINIMUM_QUANTITY - 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_upper_bound_qty(self):
    item = self.create_test_instance(**self.data)
    item.quantity = constants.MAXIMUM_QUANTITY + 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_lower_bound_shelf_life(self):
    item = self.create_test_instance(**self.data)
    item.shelf_life = Item.MINIMUM_SHELF_LIFE - 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_upper_bound_shelf_life(self):
    item = self.create_test_instance(**self.data)
    item.shelf_life = Item.MAXIMUM_SHELF_LIFE + 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_two_users_with_the_same_item_name(self):
    item1 = self.create_test_instance(**self.data)

    self.create_second_test_set()
    second_item_data = dict(self.data)
    second_item_data['user'] = self.user2
    second_item_data['shelf'] = self.shelf2
    second_item_data['preferred_stores'] = [self.store2]
    item2 = self.create_test_instance(**second_item_data)

    self.assertEqual(item1.name, item2.name)
    self.assertNotEqual(item1, item2)

  def test_default_fraction_bool(self):
    item1 = self.create_test_instance(**self.data)
    self.assertFalse(item1.has_partial_quantities)

  def test_toggle_fraction_bool(self):
    item1 = self.create_test_instance(**self.data)
    item1.has_partial_quantities = True
    item1.save()
    self.assertTrue(item1.has_partial_quantities)


@freeze_time("2020-01-14")
class TestItemCalculatedProperties(ItemTestHarness):
  """Test the Item model's calculated properties."""

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.fields = {"name": 255}
    cls.data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3,
    }

  @patch(item_module.__name__ + ".Inventory.objects.get_expired")
  def test_expired(self, m_func):
    m_func.return_value = "return_value"
    item = self.create_test_instance(**self.data)
    self.assertEqual(item.expired_new, "return_value")
    m_func.assert_called_with(item)

  @patch(item_module.__name__ + ".Inventory.objects.get_next_expiry_date")
  def test_next_expiry_date(self, m_func):
    m_func.return_value = "return_value"
    item = self.create_test_instance(**self.data)
    self.assertEqual(item.next_expiry_date_new, "return_value")
    m_func.assert_called_with(item)

  @patch(item_module.__name__ + ".Inventory.objects.get_next_expiry_quantity")
  def test_next_expiry_quantity(self, m_func):
    m_func.return_value = "return_value"
    item = self.create_test_instance(**self.data)
    self.assertEqual(item.next_expiry_quantity_new, "return_value")
    m_func.assert_called_with(item)

  @patch(item_module.__name__ + ".Inventory.objects.get_quantity")
  def test_quantity(self, m_func):
    m_func.return_value = "return_value"
    item = self.create_test_instance(**self.data)
    self.assertEqual(item.quantity_new, "return_value")
    m_func.assert_called_with(item)
