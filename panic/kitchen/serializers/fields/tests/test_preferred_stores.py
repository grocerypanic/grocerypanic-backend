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

  def test_deserialize(self):
    item = self.create_test_instance(**self.create_data)
    serialized = self.serializer(item)
    deserialized = serialized.data
    excluded_fields = [
        'user',
        '_expired',
        '_next_expiry_quantity',
    ]

    self.assertDictEqual(
        self._represent_item_as_create_data(item, exclude=excluded_fields),
        deserialized
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

    representation = self._represent_item_as_serializer_data(item)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, self.serializer_data)

  def test_serialize_ps_as_instance(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_ps_as_instance,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    item = query[0]

    representation = self._represent_item_as_serializer_data(item)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, self.serializer_data)

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

    representation = self._represent_item_as_serializer_data(item)
    representation['price'] = float(item.price)

    self.assertDictEqual(representation, self.serializer_data)
