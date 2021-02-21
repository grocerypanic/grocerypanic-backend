"""Test the Suggested Item serializer."""

from rest_framework.serializers import ValidationError

from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_suggested import SuggestedItemTestHarness
from .. import DUPLICATE_OBJECT_MESSAGE
from ..suggested import SuggestedItemSerializer


class TestItemList(SerializerTestMixin, SuggestedItemTestHarness):
  """Test the Suggested Item serializer."""

  @classmethod
  def create_data_hook(cls):
    cls.fields = {"name": 255}
    cls.create_data = {"name": "Grape"}
    cls.serializer = SuggestedItemSerializer
    cls.request = MockRequest("MockUser")
    cls.test_item_name = "Red Beans"

  def test_deserialize(self):
    item = self.create_test_instance(name=self.test_item_name)

    serialized = self.serializer(item)
    self.assertEqual(serialized.data['name'], self.test_item_name)

  def test_serialize(self):
    serialized = self.serializer(data=self.create_data)
    serialized.is_valid()

    self.assertEqual(serialized.data['name'], self.create_data['name'])

  def test_unique_constraint(self):
    serialized = self.serializer(data=self.create_data,)
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(data=self.create_data,)
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['name'][0]), DUPLICATE_OBJECT_MESSAGE
    )
