"""Test the ModelAdmin for the Item model."""

from django.contrib.admin import AdminSite

from ...models.item import Item
from ...tests.fixtures.fixtures_item import ItemTestHarness
from ..item_modeladmin import ItemModelAdmin


class TestItemAdmin(ItemTestHarness):
  """Test the ItemAdmin class."""

  @classmethod
  def create_data_hook(cls):
    cls.create_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'price': 2.00,
        'quantity': 0,
    }

  def test_save_new_instance(self):
    item = Item(**self.create_data)
    admin = ItemModelAdmin(model=item, admin_site=AdminSite())

    self.assertEqual(admin.expired(item), 0)
    self.assertEqual(admin.next_expiry_datetime(item), None)
    self.assertEqual(admin.next_expiry_quantity(item), 0)
    admin.save_model(obj=item, request=None, form=None, change=None)

  def test_save_existing_instance(self):
    item = Item(**self.create_data)
    item.save()

    admin = ItemModelAdmin(model=item, admin_site=AdminSite())

    self.assertEqual(admin.expired(item), 0)
    self.assertEqual(admin.next_expiry_datetime(item), None)
    self.assertEqual(admin.next_expiry_quantity(item), 0)
    admin.save_model(obj=item, request=None, form=None, change=None)
