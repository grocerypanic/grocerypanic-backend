"""Load test data into the database."""

from ....models.item import Item
from ....models.shelf import Shelf
from ....models.store import Store

DATA_CONFIG = {
    'storename': 'TestStore',
    'shelfname': 'TestShelf1',
    'itemname': 'TestItem',
    'number_of_items': 200,
    'number_of_stores': 1,
    'preferred_store': 0
}


class DataGenerator:
  """Generate test data for the kitchen models."""

  def __init__(self, user):
    self.user = user
    self.shelf = None
    self.items = None
    self.stores = None

  def __create_shelf_data(self):
    """Generate test shelf data."""
    self.shelf = Shelf.objects.create(
        user=self.user, name=DATA_CONFIG['shelfname']
    )

  def __create_item_data(self):
    """Generate test item data."""
    self.items = []
    for i in range(0, DATA_CONFIG['number_of_items']):
      new_item = Item(
          name=DATA_CONFIG['itemname'] + str(i),
          user=self.user,
          shelf_life="99",
          shelf=self.shelf,
          price="2.00",
      )
      self.items.append(new_item)

  def __create_store_data(self):
    """Generate test store data."""
    self.stores = []
    for i in range(0, DATA_CONFIG['number_of_stores']):
      new_store = Store(user=self.user, name=DATA_CONFIG['storename'] + str(i))
      self.stores.append(new_store)

  def __save(self):
    """Call save on all generated model objects."""
    for store in Store.objects.bulk_create(self.stores):
      store.save()

    for item in Item.objects.bulk_create(self.items):
      item.preferred_stores.add(self.stores[DATA_CONFIG['preferred_store']])
      item.save()

  def generate_data(self):
    """Perform the data generation, and saves the model."""
    self.__create_shelf_data()
    self.__create_item_data()
    self.__create_store_data()
    self.__save()
