"""Test the Suggested Item serializer."""

from django.test import TestCase
from rest_framework.serializers import ValidationError

from ...models.suggested import SuggestedItem
from ...tests.fixtures.fixtures_django import MockRequest
from .. import DUPLICATE_OBJECT_MESSAGE
from ..suggested import SuggestedItemSerializer
from .fixtures.fixtures_serializers import generate_base


class TestItemList(generate_base(TestCase)):
  """Test the Suggested Item serializer."""

  def sample_item(self, name="Red Beans"):
    item = SuggestedItem.objects.create(name=name)
    self.objects.append(item)
    return item

  @classmethod
  def setUpTestData(cls):
    cls.objects = list()
    cls.serializer = SuggestedItemSerializer
    cls.fields = {"name": 255}
    cls.data = {"name": "Grape"}
    cls.request = MockRequest("MockUser")

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def test_deserialize(self):
    test_value = "Custard"
    item = self.sample_item(test_value)

    serialized = self.serializer(item)
    self.assertEqual(serialized.data['name'], test_value)

  def test_serialize(self):
    serialized = self.serializer(data=self.data)
    serialized.is_valid()

    self.assertEqual(serialized.data['name'], self.data['name'])

  def test_unique_constraint(self):
    serialized = self.serializer(data=self.data,)
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(data=self.data,)
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['name'][0]), DUPLICATE_OBJECT_MESSAGE
    )
