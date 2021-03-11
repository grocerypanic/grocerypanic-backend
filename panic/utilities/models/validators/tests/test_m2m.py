"""Test the ManyToManyRelatedValidator class."""

from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from ..m2m import ManyToManyRelatedValidator


class MockModelWithM2M:
  """A test double for Django models with M2M fields."""

  related = Mock()
  lookup: dict

  def __init__(self, pk, user, related_mock_instances=None):
    self.id = pk
    self.user = user
    self.objects = self._create_mock_model_manager()
    self._create_mock_m2m_manager(related_mock_instances)

  def get(self, pk_set):
    return [self.lookup[pk] for pk in pk_set]

  def _create_mock_model_manager(self):
    mock_model_manager = Mock()
    mock_model_manager.objects.get = self.get
    self.lookup[self.id] = self
    return mock_model_manager

  def _create_mock_m2m_manager(self, related_mock_instances):
    mock_m2m = Mock()
    mock_m2m.objects.filter.return_value = related_mock_instances
    self.__class__.related.field.related_model = mock_m2m


class TestValidatePreferredStores(SimpleTestCase):
  """Test the ManyToManyRelatedValidator class."""

  def setUp(self):
    super().setUp()
    self.mock_user1 = Mock()
    self.mock_user2 = Mock()
    lookup_dictionary = dict()

    class MockModel(MockModelWithM2M):
      lookup = lookup_dictionary

    self.mock_model1 = MockModel(1, self.mock_user1)
    self.mock_model2 = MockModel(2, self.mock_user1, [self.mock_model1])
    self.mock_model3 = MockModel(2, self.mock_user1, [self.mock_model1])
    self.mock_model4 = MockModel(3, self.mock_user2, [self.mock_model1])

    self.m2m_validator = ManyToManyRelatedValidator(
        related_field='related',
        match_field='user',
    )

  def test_preferred_stores_correct_owner(self):
    self.m2m_validator.validate(self.mock_model1, {2, 3})

  def test_preferred_stores_incorrect_owner(self):
    with self.assertRaises(ValidationError) as raised:
      self.m2m_validator.validate(self.mock_model4, {1})

    self.assertDictEqual(
        raised.exception.message_dict, {
            'user': ["This must match the 'related' field."],
            'related': ["These selections must match the 'user' field."],
        }
    )

  def test_get_instance_value(self):
    value = self.m2m_validator.get_instance_value(self.mock_model3)
    self.assertEqual(
        value,
        self.mock_model3.user,
    )

  def test_get_related_value(self):
    value = self.m2m_validator.get_related_value(self.mock_model3)
    self.assertEqual(
        value,
        self.mock_model1.user,
    )
