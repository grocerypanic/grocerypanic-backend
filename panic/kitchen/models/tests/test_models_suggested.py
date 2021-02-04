"""Test the ItemList Model."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..suggested import SuggestedItem


class TestItemList(TestCase):

  def sample_item(self, name="Red Beans"):
    """Create a test user account."""
    item = SuggestedItem.objects.create(name=name)
    self.objects.append(item)
    return item

  @staticmethod
  def generate_overload(fields):
    return_value = []
    for key, value in fields.items():
      return_value.append({key: "abc" * value})
    return return_value

  @classmethod
  def setUpTestData(cls):
    cls.fields = {"name": 255}

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def testAddItem(self):
    test_name = "Custard"
    _ = self.sample_item(test_name)

    query = SuggestedItem.objects.filter(name=test_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, test_name)

  def testUnique(self):
    test_name = "Custard"
    _ = self.sample_item(test_name)

    with self.assertRaises(ValidationError):
      _ = self.sample_item(test_name)

    query = SuggestedItem.objects.filter(name=test_name)
    assert len(query) == 1

  def testItemInjection(self):
    test_name = "Broccoli<script>alert('hi');</script>"
    sanitized_name = "Broccoli&lt;script&gt;alert('hi');&lt;/script&gt;"

    _ = self.sample_item(test_name)

    query = SuggestedItem.objects.filter(name=sanitized_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, sanitized_name)

  def testStr(self):
    test_name = "Beer"
    item = self.sample_item(test_name)

    self.assertEqual(test_name, str(item))

  def testFieldLengths(self):
    for overloaded_field in self.generate_overload(self.fields):
      local_data = {"name": "Ice Cream"}
      local_data.update(overloaded_field)
      with self.assertRaises(ValidationError):
        _ = self.sample_item(**local_data)
