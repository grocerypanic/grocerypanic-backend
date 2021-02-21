"""Shared Shelf model test fixtures."""

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase
from django.utils import timezone

from ...models.shelf import Shelf
from .fixture_bases import KitchenModelTestFixture

User: Model = get_user_model()


class ShelfTestHarness(KitchenModelTestFixture, TestCase):
  """Test harness for the Shelf model."""

  user1: User
  user2: User
  objects: list

  @staticmethod
  def create_instance(**kwargs):
    shelf = Shelf.objects.create(user=kwargs['user'], name=kwargs['name'])
    shelf.save()
    return shelf

  @staticmethod
  def create_dependencies(seed, **kwargs):  # pylint: disable=unused-argument
    user = get_user_model().objects.create_user(
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
    shelf = self.__class__.create_instance(**kwargs)
    self.objects.append(shelf)
    return shelf

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

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()
