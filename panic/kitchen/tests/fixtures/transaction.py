"""Shared Transaction Test Fixtures for Kitchen"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store
from ...models.transaction import Transaction
from .abc_model_fixture import KitchenModelTestFixture


class TransactionTestHarness(KitchenModelTestFixture, TestCase):
  item = None
  user = None
  objects = None

  @staticmethod
  def create_instance(**kwargs):
    """Create a test item."""
    transaction = Transaction.objects.create(
        item=kwargs['item'],
        user=kwargs['user'],
        datetime=kwargs['date_object'],
        quantity=kwargs['quantity'],
    )
    return transaction

  @staticmethod
  def create_dependencies(seed):
    user = get_user_model().objects.create_user(
        username=f"testuser{seed}",
        email=f"test{seed}@niallbyrne.ca",
        password="test123",
    )
    store = Store.objects.create(
        user=user,
        name=f"store{seed}",
    )
    shelf = Shelf.objects.create(
        user=user,
        name=f"shelf{seed}",
    )
    item = Item.objects.create(
        name=f"item{seed}",
        shelf_life=99,
        user=user,
        shelf=shelf,
        price=2.00,
        quantity=3,
    )
    item.preferred_stores.add(store)
    item.save()

    return {
        "user": user,
        "store": store,
        "shelf": shelf,
        "item": item,
    }

  @classmethod
  def create_data_hook(cls):
    pass

  def create_another_user(self, seed):
    new_user = get_user_model().objects.create_user(
        username=f"testuser{seed}",
        email=f"test{seed}@niallbyrne.ca",
        password="test123",
    )
    self.objects.append(new_user)
    return new_user

  def create_test_instance(self, **kwargs):
    """Create a test item."""
    transaction = self.__class__.create_instance(**kwargs)
    self.objects.append(transaction)
    return transaction

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data = cls.create_dependencies(1)
    cls.user = test_data['user']
    cls.store = test_data['store']
    cls.shelf = test_data['shelf']
    cls.item = test_data['item']
    cls.create_data_hook()

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()
