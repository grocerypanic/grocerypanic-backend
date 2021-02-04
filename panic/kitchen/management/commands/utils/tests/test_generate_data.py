"""Test DataGenerator Class"""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..... import management
from .....models.item import Item
from .....models.shelf import Shelf
from .....models.store import Store
from ..generate_testdata import DATA_CONFIG, DataGenerator

with patch(
    management.__name__ + '.commands.utils.generate_testdata.DATA_CONFIG'
) as preset:
  BULK_SIZE = 10
  preset.return_value = DATA_CONFIG.update({
      'number_of_items': BULK_SIZE,
      'number_of_stores': BULK_SIZE
  },)

  class TestGenerateData(TestCase):

    @classmethod
    def setUpTestData(cls):
      cls.user = get_user_model().objects.create_user(
          username="created_test_user",
          email="created_test_user@niallbyrne.ca",
          password="test123",
      )
      cls.generator = DataGenerator(cls.user)

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
      self.assertEqual(shelf[0].name, DATA_CONFIG['shelfname'])

    def test_valid_user_specified_item_is_valid(self):
      store = Store.objects.get(
          user=self.user, name=DATA_CONFIG['storename'] + "0"
      )
      shelf = Shelf.objects.get(user=self.user, name=DATA_CONFIG['shelfname'])
      items = Item.objects.filter(user=self.user)
      self.assertEqual(len(items), BULK_SIZE)

      for item in items:
        self.assertEqual(len(item.preferred_stores.all()), 1)
        self.assertEqual(item.preferred_stores.all()[0], store)
        self.assertEqual(item.shelf, shelf)
