"""Tests for the ItemSerializer's PreferredStore serializer field."""

from ....models.item import Item
from ....tests.fixtures.fixtures_django import MockRequest
from ....tests.fixtures.fixtures_item import ItemTestHarness
from ...item import ItemSerializer


class TestPreferredStore(ItemTestHarness):
  """Test the ItemSerializer's PreferredStore serializer field."""

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemSerializer
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

    cls.serializer_data = {
        'name': "Canned Beans",
        'shelf_life': 109,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
    }

    cls.serializer_data_ps_as_int = dict(cls.serializer_data)

    cls.serializer_data_ps_as_instance = dict(cls.serializer_data)
    cls.serializer_data_ps_as_instance.update({
        'preferred_stores': [cls.store1],
    })

    cls.serializer_data_ps_as_str = dict(cls.serializer_data)
    cls.serializer_data_ps_as_str.update({
        'preferred_stores': [f"{cls.store1.id}"],
    })

  @classmethod
  def setUpTestData(cls):
    test_data1 = cls.create_dependencies(2)
    cls.user2 = test_data1['user']
    cls.store2 = test_data1['store']
    cls.shelf2 = test_data1['shelf']
    super().setUpTestData()

  def _expected_serialized_value(self):
    expected = dict(self.serializer_data)
    expected['next_expiry_quantity'] = 0
    expected['expired'] = 0
    expected['next_expiry_date'] = None
    expected['next_expiry_datetime'] = None
    return expected

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

    self.assertDictEqual(
        representation,
        deserialized,
    )

  def test_serialize_ps_as_int(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_ps_as_int,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    item = query[0]

    expected = self._expected_serialized_value()
    representation = self._instance_to_dict_subset(item, expected)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, expected)

  def test_serialize_ps_as_instance(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_ps_as_instance,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(
        name=self.serializer_data_ps_as_instance['name']
    )

    assert len(query) == 1
    item = query[0]

    expected = self._expected_serialized_value()
    representation = self._instance_to_dict_subset(item, expected)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, expected)

  def test_serialize_ps_as_str(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_ps_as_str,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    item = query[0]

    expected = self._expected_serialized_value()
    representation = self._instance_to_dict_subset(item, expected)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, expected)
