"""Test the ModelAdmin form for the Item model."""

from ...tests.fixtures.fixtures_item import ItemTestHarness
from ..item_modeladmin_form import ItemAdminForm


class TestItemAdminForm(ItemTestHarness):
  """Test the ItemAdminForm class."""

  @classmethod
  def create_data_hook(cls):
    cls.create_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 0,
    }

  def test_clean(self):
    form = ItemAdminForm(self.create_data)
    form.is_valid()
    form.clean()

    self.assertEqual(
        form.instance.user,
        form.cleaned_data['user'],
    )
