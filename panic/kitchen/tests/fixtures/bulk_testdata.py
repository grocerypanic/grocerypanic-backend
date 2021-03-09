"""Bulk test data generator."""

from django.contrib.auth import get_user_model

from ...models.item import Item
from ...models.shelf import Shelf
from ...models.store import Store


class DataConfiguration:
  """Configuration for the DataGenerator class."""

  store_name = 'TestStore'
  shelf_name = 'TestShelf1'
  item_name = 'TestItem'
  number_of_items = 200
  number_of_stores = 1
  preferred_store = 0


class BulkTestDataGenerator:
  """Generate test data for the kitchen models."""

  def __init__(self, username, config=DataConfiguration()):
    self.user = get_user_model().objects.get(username=username)
    self.config = config
    self.shelf = None
    self.items = None
    self.stores = None

  def __create_shelf_data(self):
    self.shelf = Shelf.objects.create(
        user=self.user, name=self.config.shelf_name
    )

  def __create_item_data(self):
    self.items = []
    for i in range(0, self.config.number_of_items):
      new_item = Item(
          name=self.config.item_name + str(i),
          user=self.user,
          shelf_life="99",
          shelf=self.shelf,
          price="2.00",
      )
      self.items.append(new_item)

  def __create_store_data(self):
    self.stores = []
    for i in range(0, self.config.number_of_stores):
      new_store = Store(user=self.user, name=self.config.store_name + str(i))
      self.stores.append(new_store)

  def __save(self):
    for store in Store.objects.bulk_create(self.stores):
      store.save()

    for item in Item.objects.bulk_create(self.items):
      item.preferred_stores.add(self.stores[self.config.preferred_store])
      item.save()

  def generate_data(self):
    """Perform the data generation, and save the generated models."""
    self.__create_shelf_data()
    self.__create_item_data()
    self.__create_store_data()
    self.__save()
