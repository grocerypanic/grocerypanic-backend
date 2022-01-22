"""Test the ManyToManyRelatedValidator class."""

from typing import Any, Dict, List, Optional, Set, cast
from unittest.mock import Mock

from django.core.exceptions import ValidationError
from django.db.models import Model, QuerySet
from django.test import SimpleTestCase

from ..m2m import ManyToManyRelatedValidator


class MockModelWithM2M:
  """A test double for Django models with M2M fields."""

  related = Mock()
  lookup: Dict[int, Model]

  def __init__(
      self,
      pk: int,
      user: Model,
      related_mock_instances: Optional[QuerySet[Any]] = None
  ) -> None:
    self.id = pk
    self.user = user
    self.objects = self._create_mock_model_manager()
    self._create_mock_m2m_manager(related_mock_instances)

  def get(self, pk_set: Set[int]) -> List[Model]:
    return [self.lookup[pk] for pk in pk_set]

  def _create_mock_model_manager(self) -> Mock:
    mock_model_manager = Mock()
    mock_model_manager.objects.get = self.get
    self.lookup[self.id] = cast(Model, self)
    return mock_model_manager

  def _create_mock_m2m_manager(
      self, related_mock_instances: QuerySet[Any]
  ) -> None:
    mock_m2m = Mock()
    mock_m2m.objects.filter.return_value = related_mock_instances
    self.__class__.related.field.related_model = mock_m2m


class TestValidatePreferredStores(SimpleTestCase):
  """Test the ManyToManyRelatedValidator class."""

  def setUp(self) -> None:
    super().setUp()
    self.mock_user1 = Mock()
    self.mock_user2 = Mock()
    lookup_dictionary: Dict[int, Model] = dict()

    class MockModel(MockModelWithM2M):
      lookup = lookup_dictionary

    self.mock_model1 = cast(Model, MockModel(1, self.mock_user1))
    self.mock_model2 = cast(
        Model,
        MockModel(2, self.mock_user1, cast(QuerySet[Any], [self.mock_model1]))
    )
    self.mock_model3 = cast(
        Model,
        MockModel(2, self.mock_user1, cast(QuerySet[Any], [self.mock_model1]))
    )
    self.mock_model4 = cast(
        Model,
        MockModel(3, self.mock_user2, cast(QuerySet[Any], [self.mock_model1]))
    )

    self.m2m_validator = ManyToManyRelatedValidator(
        related_field='related',
        match_field='user',
    )

  def test_preferred_stores_correct_owner(self) -> None:
    self.m2m_validator.validate(self.mock_model1, {2, 3})

  def test_preferred_stores_incorrect_owner(self) -> None:
    with self.assertRaises(ValidationError) as raised:
      self.m2m_validator.validate(self.mock_model4, {1})

    self.assertDictEqual(
        raised.exception.message_dict, {
            'user': ["This must match the 'related' field."],
            'related': ["These selections must match the 'user' field."],
        }
    )

  def test_get_instance_value(self) -> None:
    value = self.m2m_validator.get_instance_value(self.mock_model3)
    self.assertEqual(
        value,
        self.mock_model3.user,  # type: ignore
    )

  def test_get_related_value(self) -> None:
    value = self.m2m_validator.get_related_value(self.mock_model3)
    self.assertEqual(
        value,
        self.mock_model1.user,  # type: ignore
    )
