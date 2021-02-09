"""Shared Inventory Test Fixtures for Kitchen"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ...models.inventory import Inventory
from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store
from ...models.transaction import Transaction
from .bases import KitchenModelTestFixture


class InventoryTestHarness(KitchenModelTestFixture, TestCase):
  item1 = None
  user1 = None
  transaction1 = None
  objects = None
  today = None
  initial_quantity = 3

  @staticmethod
  def create_instance(**kwargs):
    """Create a test inventory."""
    inventory = Inventory.objects.create(
        item=kwargs['item'],
        remaining=kwargs['remaining'],
        transaction=kwargs['transaction'],
    )
    return inventory

  @staticmethod
  def create_transaction_instance(**kwargs):
    """Create a test transaction."""
    transaction = Transaction.objects.create(
        item=kwargs['item'],
        datetime=kwargs['date_object'],
        quantity=kwargs['quantity'],
    )
    return transaction

  @staticmethod
  def create_dependencies(seed, datetime_object, quantity):
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
        quantity=0,
    )
    transaction = Transaction.objects.create(
        item=item,
        datetime=datetime_object,
        quantity=quantity,
    )

    item.preferred_stores.add(store)
    item.save()

    return {
        "user": user,
        "store": store,
        "shelf": shelf,
        "item": item,
        "transaction": transaction,
    }

  @classmethod
  def create_data_hook(cls):
    pass

  def create_test_instance(self, **kwargs):
    """Create a test inventory."""
    inventory = self.__class__.create_instance(**kwargs)
    self.objects.append(inventory)
    return inventory

  def create_test_transaction_instance(self, **kwargs):
    """Create a test transaction."""
    transaction = self.__class__.create_transaction_instance(**kwargs)
    self.objects.append(transaction)
    return transaction

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data = cls.create_dependencies(1, cls.today, cls.initial_quantity)
    cls.user1 = test_data['user']
    cls.store1 = test_data['store']
    cls.shelf1 = test_data['shelf']
    cls.item1 = test_data['item']
    cls.transaction1 = test_data['transaction']
    cls.create_data_hook()

  def setUp(self):
    self.item1.quantity = self.initial_quantity
    self.item1.save()
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()
