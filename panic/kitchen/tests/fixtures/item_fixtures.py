"""Shared Item Test Fixtures for Kitchen"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store


class ItemTestHarness(TestCase):
  user1 = None
  shelf1 = None
  store1 = None
  user2 = None
  shelf2 = None
  store2 = None
  objects = None

  @staticmethod
  def create_item(**kwargs):
    """Create a test item."""
    item = Item.objects.create(
        name=kwargs['name'],
        user=kwargs['user'],
        shelf_life=kwargs['shelf_life'],
        shelf=kwargs['shelf'],
        price=kwargs['price'],
        quantity=kwargs['quantity'],
    )
    item.preferred_stores.add(kwargs['preferred_store'])
    item.save()
    return item

  @staticmethod
  def create_item_dependencies(seed):
    user = get_user_model().objects.create_user(
        username=f"testuser{seed}",
        email=f"test{seed}@niallbyrne.ca",
        password="test123",
    )

    store = Store.objects.create(
        user=user,
        name=f"Store{seed}",
    )

    shelf = Shelf.objects.create(
        user=user,
        name=f"Shelf{seed}",
    )

    return {
        "user": user,
        "store": store,
        "shelf": shelf,
    }

  @classmethod
  def create_items_hook(cls):
    pass

  def sample_item(self, **kwargs):
    """Create a test item."""
    item = self.__class__.create_item(**kwargs)
    self.objects.append(item)
    return item

  def create_second_test_set(self):
    test_data1 = self.__class__.create_item_dependencies(2)
    self.user2 = test_data1['user']
    self.store2 = test_data1['store']
    self.shelf2 = test_data1['shelf']
    self.objects = self.objects + [self.user2, self.store2, self.shelf2]

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data1 = cls.create_item_dependencies(1)
    cls.user1 = test_data1['user']
    cls.store1 = test_data1['store']
    cls.shelf1 = test_data1['shelf']
    cls.create_items_hook()

  def setUp(self):
    self.objects = list()

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()
