"""Shared Store model test fixtures."""

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.utils import timezone

from ...models.store import Store
from .fixture_bases import KitchenModelTestFixture, MutableSignalsBaseTestCase

User: Model = get_user_model()


class StoreTestHarness(KitchenModelTestFixture, MutableSignalsBaseTestCase):
  """Test harness for the Store model."""

  mute_signals = True

  user1: User
  user2: User
  objects: list

  @staticmethod
  def create_instance(**kwargs):
    store = Store.objects.create(user=kwargs['user'], name=kwargs['name'])
    store.save()
    return store

  @staticmethod
  def create_dependencies(seed, **kwargs):  # pylint: disable=unused-argument
    user = User.objects.create_user(
        username=f"testuser{seed}",
        email=f"test{seed}@niallbyrne.ca",
        password="test123",
    )

    return {
        "user": user,
    }

  @classmethod
  def create_data_hook(cls):
    pass

  def create_test_instance(self, **kwargs):
    store = self.__class__.create_instance(**kwargs)
    self.objects.append(store)
    return store

  def create_second_test_set(self):
    test_data1 = self.__class__.create_dependencies(2)
    self.user2 = test_data1['user']
    self.objects = self.objects + [self.user2]

  @classmethod
  def setUpTestData(cls):
    cls.today = timezone.now()
    test_data1 = cls.create_dependencies(1)
    cls.user1 = test_data1['user']
    cls.create_data_hook()
