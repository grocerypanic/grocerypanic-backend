"""Test the Suggested Item serializer."""

from rest_framework.serializers import ValidationError

from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_suggested import SuggestedItemTestHarness
from ..constants import DUPLICATE_OBJECT_MSG
from ..suggested import SuggestedItem, SuggestedItemSerializer


class TestItemList(SerializerTestMixin, SuggestedItemTestHarness):
  """Test the Suggested Item serializer."""

  serializer_data: dict
  fields: dict

  @classmethod
  def create_data_hook(cls):
    cls.serializer = SuggestedItemSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest("MockUser")

    cls.calculated_properties = set()
    cls.m2m_fields = set()

    cls.create_data = {
        "name": "Grape",
    }

    cls.serializer_data = {
        "name": "Grape",
    }

  def test_deserialize(self):
    item = self.create_test_instance(**self.create_data)
    serialized = self.serializer(item)
    representation = self._instance_to_dict(item, exclude=['user'])

    self.assertEqual(serialized.data, representation)

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = SuggestedItem.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    suggested = query[0]

    expected = dict(self.serializer_data)
    representation = self._instance_to_dict_subset(suggested, expected)

    self.assertDictEqual(representation, expected)

  def test_unique_constraint(self):
    serialized = self.serializer(data=self.serializer_data,)
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(data=self.create_data,)
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(str(serialized2.errors['name'][0]), DUPLICATE_OBJECT_MSG)
