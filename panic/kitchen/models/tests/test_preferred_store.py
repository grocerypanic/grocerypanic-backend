"""Test the PreferredStore model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixtures_item import ItemTestHarness
from ..preferred_store import PreferredStore


class TestPreferredStore(ItemTestHarness):
  """Test the PreferredStore model."""

  @classmethod
  def create_data_hook(cls):
    cls.create_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
    }

  def test_create(self):
    item = self.create_test_instance(**self.create_data)
    preferred_stores = PreferredStore.objects.filter(item=item)

    self.assertEqual(
        len(preferred_stores),
        len(item.preferred_stores.all()),
    )

    self.assertEqual(
        preferred_stores.first().store, item.preferred_stores.first()
    )

    self.assertEqual(
        preferred_stores.first().item,
        item,
    )

  def test_str(self):
    item = self.create_test_instance(**self.create_data)
    store = item.preferred_stores.all().first()
    preferred_store = PreferredStore.objects.filter(item=item).first()

    self.assertEqual(
        f"{item}'s preferred store: {store}",
        str(preferred_store),
    )

  def test_validation_error(self):
    second_data_set = self.create_dependencies(2)
    store = second_data_set['store']

    wrong_related_item = dict(self.create_data)
    wrong_related_item.update({'preferred_stores': [store]})

    with self.assertRaises(ValidationError) as raised:
      self.create_test_instance(**wrong_related_item)

    self.assertDictEqual(
        raised.exception.message_dict, {
            'user': ["This must match the 'preferred_stores' field."],
            'preferred_stores':
                ["These selections must match the 'user' field."],
        }
    )
