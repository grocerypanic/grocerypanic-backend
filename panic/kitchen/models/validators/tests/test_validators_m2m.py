"""Test the Item model's custom validators."""

from django.core.exceptions import ValidationError

from ....tests.fixtures.fixtures_item import ItemTestHarness
from ..m2m import ManyToManyValidator


class TestValidatePreferredStores(ItemTestHarness):
  """Test the preferred_stores_validator function."""

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
    self.item = self.create_test_instance(**self.create_data)
    self.m2m_validator = ManyToManyValidator(
        related_field='preferred_stores',
        match_field='user',
    )

  def test_preferred_stores_correct_owner(self):
    self.m2m_validator.validate(self.item, {self.store1.id})

  def test_preferred_stores_incorrect_owner(self):
    with self.assertRaises(ValidationError) as raised:
      self.m2m_validator.validate(self.item, {self.store2.id})

    self.assertDictEqual(
        raised.exception.message_dict, {
            'user': ["This must match the 'preferred_stores' field."],
            'preferred_stores':
                ["These selections must match the 'user' field."],
        }
    )
