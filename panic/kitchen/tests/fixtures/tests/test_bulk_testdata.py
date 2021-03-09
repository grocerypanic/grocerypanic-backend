"""Test the BulkTestDataGenerator class."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from ....models.item import Item
from ....models.shelf import Shelf
from ....models.store import Store
from ..bulk_testdata import BulkTestDataGenerator, DataConfiguration

BULK_SIZE = 3


class TestDataConfiguration(DataConfiguration):
  """Test configuration for data generation."""

  number_of_items = BULK_SIZE
  number_of_stores = BULK_SIZE


class TestBulkTestDataGenerator(TestCase):
  """Test the BulkTestDataGenerator class."""

  @classmethod
  def setUpTestData(cls):
    cls.user = get_user_model().objects.create_user(
        username="created_test_user",
        email="created_test_user@niallbyrne.ca",
        password="test123",
    )
    cls.test_config = TestDataConfiguration()
    cls.generator = BulkTestDataGenerator(
        cls.user.username,
        config=cls.test_config,
    )

  def setUp(self):
    self.generator.generate_data()

  def tearDown(self):
    for item in Item.objects.filter(user=self.user):
      item.delete()
    for shelf in Shelf.objects.filter(user=self.user):
      shelf.delete()
    for store in Store.objects.filter(user=self.user):
      store.delete()

  def test_valid_user_specified_store_is_valid(self):
    stores = Store.objects.filter(user=self.user)
    self.assertEqual(len(stores), BULK_SIZE)

  def test_valid_user_specified_shelf_is_valid(self):
    shelf = Shelf.objects.filter(user=self.user)
    self.assertEqual(len(shelf), 1)
    self.assertEqual(shelf[0].name, self.test_config.shelf_name)

  def test_valid_user_specified_item_is_valid(self):
    store = Store.objects.get(
        user=self.user, name=self.test_config.store_name + "0"
    )
    shelf = Shelf.objects.get(user=self.user, name=self.test_config.shelf_name)
    items = Item.objects.filter(user=self.user)
    self.assertEqual(len(items), BULK_SIZE)

    for item in items:
      self.assertEqual(len(item.preferred_stores.all()), 1)
      self.assertEqual(item.preferred_stores.all()[0], store)
      self.assertEqual(item.shelf, shelf)
