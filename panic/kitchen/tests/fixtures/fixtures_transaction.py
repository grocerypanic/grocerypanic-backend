"""Shared Transaction model test fixtures."""

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


class TransactionTestHarness(
    KitchenModelTestFixture, MutableSignalsBaseTestCase
):
  """Test harness for the Transaction model."""

  mute_signals = True

  item1: Item
  user1: User
  objects: list
  today: datetime
  initial_quantity = 0

  @staticmethod
  def create_instance(**kwargs):
    transaction = Transaction.objects.create(
        item=kwargs['item'],
        datetime=kwargs['date_object'],
        quantity=kwargs['quantity'],
    )
    return transaction

  @staticmethod
  def create_dependencies(seed, **kwargs):  # pylint: disable=unused-argument
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
    new_user = User.objects.create_user(
        username=f"testuser{seed}",
        email=f"test{seed}@niallbyrne.ca",
        password="test123",
    )
    self.objects.append(new_user)
    return new_user

  def create_test_instance(self, **kwargs):
    transaction = self.__class__.create_instance(**kwargs)
    self.objects.append(transaction)
    return transaction

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data = cls.create_dependencies(1)
    cls.user1 = test_data['user']
    cls.store1 = test_data['store']
    cls.shelf1 = test_data['shelf']
    cls.item1 = test_data['item']
    cls.create_data_hook()

  def reset_item1(self):
    self.item1.quantity = 0
    self.item1.save()
    Inventory.objects.filter(item=self.item1).delete()

  def setUp(self):
    self.reset_item1()
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()
