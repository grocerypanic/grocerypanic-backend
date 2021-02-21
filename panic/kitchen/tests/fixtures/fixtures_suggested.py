"""Shared Suggested Item model test fixtures."""

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase

from ...models.suggested import SuggestedItem
from .fixture_bases import KitchenModelTestFixture

User: Model = get_user_model()


class SuggestedItemTestHarness(KitchenModelTestFixture, TestCase):
  """Test harness for the Suggested Item model."""

  user1: User
  user2: User
  objects: list

  @staticmethod
  def create_instance(**kwargs):
    suggested = SuggestedItem.objects.create(name=kwargs['name'])
    suggested.save()
    return suggested

  @staticmethod
  def create_dependencies(seed, **kwargs):  # pylint: disable=unused-argument
    pass

  @classmethod
  def create_data_hook(cls):
    pass

  def create_test_instance(self, **kwargs):
    suggested = self.__class__.create_instance(**kwargs)
    self.objects.append(suggested)
    return suggested

  @classmethod
  def setUpTestData(cls):
    cls.create_dependencies(1)
    cls.create_data_hook()

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()
