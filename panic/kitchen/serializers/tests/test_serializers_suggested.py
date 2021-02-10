"""Test the Suggested Item Serializer."""

from django.test import TestCase
from rest_framework.serializers import ValidationError

from ...models.suggested import SuggestedItem
from .. import DUPLICATE_OBJECT_MESSAGE
from ..suggested import SuggestedItemSerializer


class TestItemList(TestCase):

  def sample_item(self, name="Red Beans"):
    """Create a test item."""
    item = SuggestedItem.objects.create(name=name)
    self.objects.append(item)
    return item

  @staticmethod
  def generate_overload(fields):
    return_list = []
    for key, value in fields.items():
      overloaded = dict()
      overloaded[key] = "abc" * value
      return_list.append(overloaded)
    return return_list

  @classmethod
  def setUpTestData(cls):
    cls.objects = list()
    cls.serializer = SuggestedItemSerializer
    cls.fields = {"name": 255}

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def testDeserialize(self):
    test_value = "Custard"
    item = self.sample_item(test_value)

    serialized = self.serializer(item)
    self.assertEqual(serialized.data['name'], test_value)

  def testSerialize(self):
    test_value = {"name": "Grape"}
    serialized = self.serializer(data=test_value)
    serialized.is_valid()

    self.assertEqual(serialized.data['name'], test_value['name'])

  def testUniqueConstraint(self):
    test_value = {"name": "Grape"}

    serialized = self.serializer(data=test_value,)
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(data=test_value,)
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['name'][0]), DUPLICATE_OBJECT_MESSAGE
    )

  def testFieldLengths(self):
    overloads = self.generate_overload(self.fields)
    for overload in overloads:
      with self.assertRaises(ValidationError):
        serialized = self.serializer(data=overload)
        serialized.is_valid(raise_exception=True)
