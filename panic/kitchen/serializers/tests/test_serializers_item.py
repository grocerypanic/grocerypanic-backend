"""Test the Item serializer."""

from rest_framework.serializers import ErrorDetail, ValidationError

from ...exceptions import ValidationPermissionError
from ...models.item import Item
from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_item import ItemTestHarness
from .. import DUPLICATE_OBJECT_MESSAGE
from ..item import ItemSerializer


class TestItem(SerializerTestMixin, ItemTestHarness):
  """Test the Item serializer."""

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)

    cls.create_data = {
        'name': "Canned Beans",
        'shelf_life': 99,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
    }
    cls.serializer_data = {
        'name': "Canned Beans",
        'shelf_life': 109,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data_wrong_shelf = {
        'name': "Canned Beans",
        'shelf_life': 109,
        'shelf': cls.shelf2.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data_wrong_store = {
        'name': "Canned Beans",
        'shelf_life': 109,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store2.id],
        'price': 2.00,
        'quantity': 3
    }

  @classmethod
  def setUpTestData(cls):
    test_data1 = cls.create_dependencies(2)
    cls.user2 = test_data1['user']
    cls.store2 = test_data1['store']
    cls.shelf2 = test_data1['shelf']
    super().setUpTestData()

  def test_deserialize(self):
    item = self.create_test_instance(**self.create_data)
    serialized = self.serializer(item)
    deserialized = serialized.data

    price = '2.00'

    self.assertEqual(deserialized['name'], self.create_data['name'])
    self.assertFalse(deserialized['has_partial_quantities'])
    self.assertEqual(deserialized['shelf_life'], self.create_data['shelf_life'])
    self.assertEqual(deserialized['shelf'], self.shelf1.id)
    self.assertEqual(deserialized['price'], price)
    self.assertEqual(deserialized['quantity'], 0)
    self.assertEqual(deserialized['expired'], 0)
    self.assertEqual(deserialized['next_expiry_quantity'], 0)
    self.assertEqual(deserialized['next_expiry_date'], None)
    preferred_stores = [store.id for store in item.preferred_stores.all()]
    self.assertListEqual(deserialized['preferred_stores'], preferred_stores)
    assert 'user' not in deserialized

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    item = query[0]

    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.shelf_life, self.serializer_data['shelf_life'])
    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.shelf.id, self.shelf1.id)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, 0)
    self.assertFalse(item.has_partial_quantities)

  def test_serialize_fractional_quantities(self):
    fractional_quantities = dict(self.serializer_data)
    fractional_quantities.update({
        "has_partial_quantities": True,
    },)

    serialized = self.serializer(
        context={'request': self.request},
        data=fractional_quantities,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=fractional_quantities['name'])

    assert len(query) == 1
    item = query[0]

    self.assertTrue(item.has_partial_quantities)

  def test_serialize_wrong_shelf(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_wrong_shelf,
    )
    with self.assertRaises(ValidationError) as raised:
      serialized.is_valid(raise_exception=True)

    self.assertEqual(
        raised.exception.detail,
        {
            'shelf': [
                ErrorDetail(
                    string="Please provide a valid shelf.",
                    code=ValidationPermissionError.default_code
                ),
            ],
        },
    )

  def test_serialize_wrong_store(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_wrong_store,
    )
    with self.assertRaises(ValidationError) as raised:
      serialized.is_valid(raise_exception=True)

    self.assertEqual(
        raised.exception.detail,
        {
            'preferred_stores': [
                ErrorDetail(
                    string="Please provide valid preferred_stores.",
                    code=ValidationPermissionError.default_code
                ),
            ],
        },
    )

  def test_unique_constraint(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['non_field_errors'][0]),
        DUPLICATE_OBJECT_MESSAGE,
    )
