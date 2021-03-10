"""Test the ModelAdmin formset for the PreferredStore model."""

from django.forms import inlineformset_factory

from ...models.item import Item
from ...models.preferred_store import PreferredStore
from ...tests.fixtures.fixtures_item import ItemTestHarness
from ..preferred_store_modeladmin_form import (
    DUPLICATE_ERROR_MESSAGE,
    WRONG_USER_ERROR_MESSAGE,
    PreferredStoreAdminFormSet,
)


class TestPreferredStoreAdminFormSet(ItemTestHarness):
  """Test the PreferredStoreAdminFormSet class."""

  @classmethod
  def create_data_hook(cls):
    cls.item_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'price': 2.00,
        'quantity': 0,
        'shelf': cls.shelf1,
    }

    cls.item1 = Item(**cls.item_data)
    cls.item1.save()

    cls.preferred_store_data = {
        'store': cls.store1,
        'item': cls.item1,
    }

  def setUp(self):
    super().setUp()
    self.test_formset = inlineformset_factory(
        parent_model=Item,
        model=PreferredStore,
        formset=PreferredStoreAdminFormSet,
        exclude=(),
        extra=1
    )

  def test_valid(self):
    data = {
        'preferredstore_set-TOTAL_FORMS': '1',
        'preferredstore_set-INITIAL_FORMS': '0',
        'preferredstore_set-0-store': self.store1,
        'preferredstore_set-0-item': self.item1,
    }

    formset = self.test_formset(data, instance=self.item1, save_as_new=True)
    self.assertTrue(formset.is_valid())

  def test_invalid(self):
    self.create_second_test_set()

    data = {
        'preferredstore_set-TOTAL_FORMS': '1',
        'preferredstore_set-INITIAL_FORMS': '0',
        'preferredstore_set-0-store': self.store2,
        'preferredstore_set-0-item': self.item1,
    }

    formset = self.test_formset(data, instance=self.item1, save_as_new=True)
    self.assertFalse(formset.is_valid())
    self.assertEqual(formset.errors, [{'store': [WRONG_USER_ERROR_MESSAGE]}])

  def test_delete(self):
    data = {
        'preferredstore_set-TOTAL_FORMS': '1',
        'preferredstore_set-INITIAL_FORMS': '0',
        'preferredstore_set-0-store': self.store1,
        'preferredstore_set-0-item': self.item1,
        'preferredstore_set-0-DELETE': True,
    }
    formset = self.test_formset(data, instance=self.item1)
    self.assertTrue(formset.is_valid())

  def test_duplicate(self):
    data = {
        'preferredstore_set-TOTAL_FORMS': '2',
        'preferredstore_set-INITIAL_FORMS': '0',
        'preferredstore_set-0-store': self.store1,
        'preferredstore_set-0-item': self.item1,
        'preferredstore_set-1-store': self.store1,
        'preferredstore_set-1-item': self.item1,
    }
    formset = self.test_formset(data, instance=self.item1, save_as_new=True)
    self.assertFalse(formset.is_valid())
    self.assertEqual(formset.errors, [{}, {'store': [DUPLICATE_ERROR_MESSAGE]}])
