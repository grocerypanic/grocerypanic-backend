"""Test harness for the Item API ViewSet."""

from ....serializers.item import ItemSerializer
from ....tests.fixtures.fixtures_item import ItemTestHarness


class ItemViewSetTestHarness(ItemTestHarness):
  """Extend the test harness by adding item test data."""

  @classmethod
  def setUpTestData(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']
    cls.store2 = test_data2['store']
    cls.shelf2 = test_data2['shelf']
    super().setUpTestData()

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemSerializer
    cls.data1 = {
        'name': "Canned Beans",
        'shelf_life': 99,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3
    }
    cls.data2 = {
        'name': "Lasagna Noodles",
        'shelf_life': 104,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data = {
        'name': "Microwave Dinner",
        'shelf_life': 109,
        'user': cls.user1.id,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data_wrong_shelf = {
        'name': "Japanese Ramen",
        'shelf_life': 110,
        'user': cls.user2.id,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store2.id],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data_wrong_store = {
        'name': "Japanese Ramen",
        'shelf_life': 110,
        'user': cls.user2.id,
        'shelf': cls.shelf2.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
        'quantity': 3
    }
