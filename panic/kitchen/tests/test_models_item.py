"""Test the Item Model."""

from django.core.exceptions import ValidationError

from ..models.item import (
    MAXIMUM_QUANTITY,
    MAXIMUM_SHELF_LIFE,
    MINIMUM_QUANTITY,
    MINIMUM_SHELF_LIFE,
    Item,
)
from .fixtures.item import ItemTestHarness


class TestItem(ItemTestHarness):

  @classmethod
  def create_items_hook(cls):
    cls.fields = {"name": 255}
    cls.data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_store': cls.store1,
        'price': 2.00,
        'quantity': 3,
    }

  @staticmethod
  def generate_overload(fields):
    return_value = []
    for key, value in fields.items():
      return_value.append({key: "abc" * value})
    return return_value

  def testAddItem(self):
    created = self.sample_item(**self.data)
    query = Item.objects.filter(name=self.data['name'])

    self.assertQuerysetEqual(query, map(repr, [created]))

  def testUnique(self):
    _ = self.sample_item(**self.data)

    with self.assertRaises(ValidationError):
      _ = self.sample_item(**self.data)

    query = Item.objects.filter(name=self.data['name'])
    assert len(query) == 1

  def testAddItemInjection(self):
    injection_attack = dict(self.data)
    injection_attack['name'] = "Canned Beans<script>alert('hi');</script>"
    sanitized_name = "Canned Beans&lt;script&gt;alert('hi');&lt;/script&gt;"

    _ = self.sample_item(**injection_attack)

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

  def testStr(self):
    item = self.sample_item(**self.data)
    self.assertEqual(self.data['name'], str(item))

  def testFieldLengths(self):
    for overloaded_field in self.generate_overload(self.fields):
      local_data = dict(self.data)
      local_data.update(overloaded_field)
      with self.assertRaises(ValidationError):
        _ = self.sample_item(**local_data)

  def testNegativeQuantity(self):
    item = self.sample_item(**self.data)
    item.quantity = -5
    assert item.quantity < MINIMUM_QUANTITY
    with self.assertRaises(ValidationError):
      item.save()

  def testEnormousQuantity(self):
    item = self.sample_item(**self.data)
    item.quantity = 9000000
    assert item.quantity > MAXIMUM_QUANTITY
    with self.assertRaises(ValidationError):
      item.save()

  def testShelfLifeRestrictionsLow(self):
    item = self.sample_item(**self.data)
    item.shelf_life = 0
    assert item.shelf_life < MINIMUM_SHELF_LIFE
    with self.assertRaises(ValidationError):
      item.save()

  def testShelfLifeRestrictionsHigh(self):
    item = self.sample_item(**self.data)
    item.shelf_life = 9000
    assert item.shelf_life > MAXIMUM_SHELF_LIFE
    with self.assertRaises(ValidationError):
      item.save()

  def test_next_expiry_quantity_low(self):
    item = self.sample_item(**self.data)
    item.next_expiry_quantity = -5
    assert item.next_expiry_quantity < MINIMUM_QUANTITY
    with self.assertRaises(ValidationError):
      item.save()

  def test_next_expiry_quantity_high(self):
    item = self.sample_item(**self.data)
    item.next_expiry_quantity = 9000000
    assert item.next_expiry_quantity > MAXIMUM_QUANTITY
    with self.assertRaises(ValidationError):
      item.save()

  def test_expired_low(self):
    item = self.sample_item(**self.data)
    item.expired = -5
    assert item.expired < MINIMUM_QUANTITY
    with self.assertRaises(ValidationError):
      item.save()

  def test_expired_high(self):
    item = self.sample_item(**self.data)
    item.expired = 9000000
    assert item.expired > MAXIMUM_QUANTITY
    with self.assertRaises(ValidationError):
      item.save()

  def test_two_users_with_the_same_item_name(self):
    item1 = self.sample_item(**self.data)

    self.create_second_test_set()
    second_item_data = dict(self.data)
    second_item_data['user'] = self.user2
    second_item_data['shelf'] = self.shelf2
    second_item_data['preferred_store'] = self.store2
    item2 = self.sample_item(**second_item_data)

    self.assertEqual(item1.name, item2.name)
    self.assertNotEqual(item1, item2)
