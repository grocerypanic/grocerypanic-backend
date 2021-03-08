"""Test the Django Admin Form for the Item model."""

from unittest.mock import patch

from ...signals import item as item_module
from ...tests.fixtures.fixtures_item import ItemTestHarness
from ..item_model_admin_form import ItemAdminForm


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

  @patch(item_module.__name__ + '.ManyToManyValidator.validate')
  def test_is_valid(self, m_validate):
    form = ItemAdminForm(self.create_data)
    form.is_valid()
    m_validate.assert_called_once_with(form.instance, {self.store1.id})

  @patch(item_module.__name__ + '.ManyToManyValidator.validate')
  def test_clean(self, m_validate):
    form = ItemAdminForm(self.create_data)
    form.is_valid()
    m_validate.reset_mock()

    form.clean()
    m_validate.assert_called_once_with(form.instance, {self.store1.id})

  def test_save_valid(self):
    form = ItemAdminForm(self.create_data)
    form.is_valid()
    form.save()

  def test_save_invalid(self):
    self.create_second_test_set()
    data = dict(self.create_data)
    data['preferred_stores'] = [self.store2]
    form = ItemAdminForm(data)
    form.is_valid()

    with self.assertRaises(ValueError):
      form.save()
