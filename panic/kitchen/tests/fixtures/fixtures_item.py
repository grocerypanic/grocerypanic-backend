"""Shared Item model test fixtures."""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Model
from django.forms import model_to_dict
from django.utils import timezone

from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store
from .fixture_bases import KitchenModelTestFixture, MutableSignalsBaseTestCase

User: Model = get_user_model()


class ItemTestHarness(KitchenModelTestFixture, MutableSignalsBaseTestCase):
  """Test harness for the Item model."""

  mute_signals = True

  user1: User
  shelf1: Shelf
  store1: Store
  user2: User
  shelf2: Shelf
  store2: Store
  objects: list

  @staticmethod
  def create_instance(**kwargs):
    with transaction.atomic():
      item = Item.objects.create(
          name=kwargs['name'],
          user=kwargs['user'],
          shelf_life=kwargs['shelf_life'],
          shelf=kwargs['shelf'],
          price=kwargs['price'],
      )
      for store in kwargs['preferred_stores']:
        item.preferred_stores.add(store)
      item.save()
    return item

  @staticmethod
  def create_dependencies(seed, **kwargs):  # pylint: disable=unused-argument
    user = User.objects.create_user(
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
  def create_data_hook(cls):
    pass

  def create_test_instance(self, **kwargs):
    item = self.__class__.create_instance(**kwargs)
    self.objects.append(item)
    return item

  def create_second_test_set(self):
    test_data1 = self.__class__.create_dependencies(2)
    self.user2 = test_data1['user']
    self.store2 = test_data1['store']
    self.shelf2 = test_data1['shelf']
    self.objects = self.objects + [self.user2, self.store2, self.shelf2]

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data1 = cls.create_dependencies(1)
    cls.user1 = test_data1['user']
    cls.store1 = test_data1['store']
    cls.shelf1 = test_data1['shelf']
    cls.create_data_hook()

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      if obj.id:
        obj.delete()

  @staticmethod
  def _represent_item_as_create_data(instance, exclude=()):
    representation = model_to_dict(instance,)
    representation['price'] = "%.2f" % representation['price']
    representation['next_expiry_quantity'] = instance.next_expiry_quantity
    representation['expired'] = instance.expired
    representation['next_expiry_date'] = instance.next_expiry_date
    representation['next_expiry_datetime'] = instance.next_expiry_datetime
    representation['preferred_stores'] = [
        store.id for store in instance.preferred_stores.all()
    ]
    for value in exclude:
      del representation[value]

    return representation

  def _represent_item_as_serializer_data(self, instance):
    return self._represent_item_as_create_data(
        instance,
        exclude=[
            'id',
            'quantity',
            'user',
            '_expired',
            '_next_expiry_quantity',
            'expired',
            'next_expiry_date',
            'next_expiry_datetime',
            'next_expiry_quantity',
            'has_partial_quantities',
        ]
    )
