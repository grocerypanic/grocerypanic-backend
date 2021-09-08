"""Test the Item serializer."""

from rest_framework.serializers import ErrorDetail, ValidationError

from ...exceptions import ValidationPermissionError
from ...models.item import Item
from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_item import ItemTestHarness
from ..constants import UNIQUE_CONSTRAINT_MSG
from ..item import ItemSerializer


class TestItem(SerializerTestMixin, ItemTestHarness):
  """Test the Item serializer."""

  serializer_data: dict
  fields: dict

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)

    cls.calculated_properties = {
        'expired',
        'next_expiry_date',
        'next_expiry_datetime',
        'next_expiry_quantity',
    }
    cls.m2m_fields = {'preferred_stores'}

    cls.create_data = {
        'name': "Canned Beans",
        'shelf_life': 99,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
    }

    cls.create_data_no_shelf = dict(cls.create_data)
    cls.create_data_no_shelf.update({
      'shelf': None,
    })

    cls.create_data_wrong_shelf = dict(cls.create_data)
    cls.create_data_wrong_shelf.update({
        'shelf': cls.shelf2.id,
        'preferred_stores': [cls.store1.id],
    })

    cls.create_data_wrong_store = dict(cls.create_data)
    cls.create_data_wrong_store.update({
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store2.id],
    })

    cls.serializer_data = {
        'name': "Canned Beans",
        'shelf_life': 109,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
    }

    cls.serializer_data_no_shelf = dict(cls.serializer_data)
    cls.serializer_data_no_shelf.update({
      'shelf': None,
    })

  def update_with_default_create_values(self, source_dictionary):
    new_dictionary = dict(source_dictionary)
    new_dictionary['next_expiry_quantity'] = 0
    new_dictionary['expired'] = 0
    new_dictionary['next_expiry_date'] = None
    new_dictionary['next_expiry_datetime'] = None
    return new_dictionary

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
    excluded_fields = [
        'user',
        '_expired',
        '_next_expiry_quantity',
    ]

    representation = self._instance_to_dict(item, exclude=excluded_fields)
    representation['price'] = "%.2f" % representation['price']

    self.assertDictEqual(representation, deserialized)

  def test_deserialize_no_shelf(self):
    item = self.create_test_instance(**self.create_data_no_shelf)
    serialized = self.serializer(item)
    deserialized = serialized.data
    excluded_fields = [
        'user',
        '_expired',
        '_next_expiry_quantity',
    ]

    representation = self._instance_to_dict(item, exclude=excluded_fields)
    representation['price'] = "%.2f" % representation['price']

    self.assertDictEqual(representation, deserialized)

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

    expected = self.update_with_default_create_values(self.serializer_data)
    representation = self._instance_to_dict_subset(item, expected)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, expected)

  def test_serialize_no_shelf(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_no_shelf,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data_no_shelf['name'])

    assert len(query) == 1
    item = query[0]

    expected = self.update_with_default_create_values(
      self.serializer_data_no_shelf
    )
    representation = self._instance_to_dict_subset(item, expected)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, expected)

  def test_serializer_user(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    shelf = query[0]

    self.assertEqual(shelf.user.id, self.user1.id)

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
        data=self.create_data_wrong_shelf,
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
        data=self.create_data_wrong_store,
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

  def test_case_unique_constraint(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    case_change = dict(self.serializer_data)
    case_change.update({"name": self.serializer_data['name'].lower()})

    serialized2 = self.serializer(
        context={'request': self.request},
        data=case_change,
    )
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['name'][0]),
        UNIQUE_CONSTRAINT_MSG,
    )

  def test_case_unique_constraint_update_instance(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    instance = serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        instance=instance,
        data={"name": self.serializer_data['name'].lower()},
        partial=True
    )

    serialized2.is_valid(raise_exception=True)
    serialized2.save()

    self.assertEqual(
        instance.name,
        self.serializer_data['name'].lower(),
    )
