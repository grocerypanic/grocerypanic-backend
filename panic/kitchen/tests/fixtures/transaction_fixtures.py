"""Shared Transaction Test Fixtures for Kitchen"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store
from ...models.transaction import Transaction


def create_transaction(user, item, date_object, quantity):
  """Create a test item."""
  transaction = Transaction.objects.create(
      item=item,
      user=user,
      datetime=date_object,
      quantity=quantity,
  )
  return transaction


def create_transaction_dependencies():
  user = get_user_model().objects.create_user(
      username="testuser",
      email="test@niallbyrne.ca",
      password="test123",
  )
  store = Store.objects.create(
      user=user,
      name="No Frills",
  )
  shelf = Shelf.objects.create(
      user=user,
      name="Pantry",
  )
  item = Item.objects.create(
      name="Canned Beans",
      shelf_life=99,
      user=user,
      shelf=shelf,
      price=2.00,
      quantity=3
  )
  item.preferred_stores.add(store)
  item.save()

  return {"user": user, "store": store, "shelf": shelf, "item": item}


class TransactionTestHarness(TestCase):
  item = None
  user = None
  objects = None

  @classmethod
  def create_transactions_hook(cls):
    pass

  def create_second_user(self):
    new_user = get_user_model().objects.create_user(
        username="testuser2",
        email="test2@niallbyrne.ca",
        password="test123",
    )
    self.objects.append(new_user)
    return new_user

  # pylint: disable=R0913
  def sample_transaction(self, user, item, date_object, quantity):
    """Create a test item."""
    transaction = create_transaction(user, item, date_object, quantity)
    self.objects.append(transaction)
    return transaction

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data = create_transaction_dependencies()
    cls.user = test_data['user']
    cls.store = test_data['store']
    cls.shelf = test_data['shelf']
    cls.item = test_data['item']
    cls.create_transactions_hook()