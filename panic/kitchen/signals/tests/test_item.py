"""Test The Item model signal handler.."""

from unittest.mock import patch

from ...tests.fixtures.fixtures_item import ItemTestHarness
from .. import item as item_module


class TestItemPreferredStoresValidation(ItemTestHarness):
  """Test the item_preferred_stores_validator signal handler."""

  @classmethod
  def create_data_hook(cls):
    cls.create_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [],
        'price': 2.00,
    }

  def setUp(self):
    super().setUp()
    self.create_second_test_set()

  @patch(item_module.__name__ + '.ManyToManyValidator.validate')
  def test_add(self, m_validator):
    item = self.create_test_instance(**self.create_data)
    item.preferred_stores.add(self.store1)
    m_validator.assert_called_once_with(item, {self.store1.id})

  @patch(item_module.__name__ + '.ManyToManyValidator.validate')
  def test_remove(self, m_validator):
    item = self.create_test_instance(**self.create_data)
    item.preferred_stores.add(self.store1)
    m_validator.reset_mock()

    item.preferred_stores.remove(self.store1)
    m_validator.assert_not_called()
