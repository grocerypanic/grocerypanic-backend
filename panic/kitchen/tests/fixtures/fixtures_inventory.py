"""Shared Inventory model test fixtures."""

from datetime import datetime

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.utils import timezone

from ...models.inventory import Inventory
from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store
from ...models.transaction import Transaction
from .fixture_bases import KitchenModelTestFixture, MutableSignalsBaseTestCase

User: Model = get_user_model()


class InventoryTestHarness(KitchenModelTestFixture, MutableSignalsBaseTestCase):
  """Test harness for the Inventory model."""

  item1: Item
  user1: User
  transaction1: Transaction
  objects: list
  today: datetime
  initial_quantity = 3

  @staticmethod
  def create_instance(**kwargs):
    inventory = Inventory.objects.create(
        item=kwargs['item'],
        remaining=kwargs['remaining'],
        transaction=kwargs['transaction'],
    )
    return inventory

  @staticmethod
  def create_transaction_instance(**kwargs):
    transaction = Transaction.objects.create(
        item=kwargs['item'],
        datetime=kwargs['date_object'],
        quantity=kwargs['quantity'],
    )
    return transaction

  @staticmethod
  def create_dependencies(seed, **kwargs):
    datetime_object = kwargs['datetime_object']
    quantity = kwargs['quantity']

    user = User.objects.create_user(
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
    inventory = self.__class__.create_instance(**kwargs)
    self.objects.append(inventory)
    return inventory

  def create_test_transaction_instance(self, **kwargs):
    transaction = self.__class__.create_transaction_instance(**kwargs)
    self.objects.append(transaction)
    return transaction

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()

    dependency_kwargs = {
        'datetime_object': cls.today,
        'quantity': cls.initial_quantity
    }
    test_data = cls.create_dependencies(1, **dependency_kwargs)
    cls.user1 = test_data['user']
    cls.store1 = test_data['store']
    cls.shelf1 = test_data['shelf']
    cls.item1 = test_data['item']

    cls.transaction1 = test_data['transaction']
    cls.create_data_hook()
