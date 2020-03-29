"""Test the ItemList Model."""

from django.db.utils import DataError
from django.test import TestCase

from ..models.itemlist import ItemList


class TestItemList(TestCase):

  def sample_item(self, name="Red Beans"):
    """Create a test user account."""
    item = ItemList.objects.create(name=name)
    self.objects.append(item)
    return item

  @staticmethod
  def generate_overload(fields):
    return_value = {}
    for key, value in fields.items():
      return_value[key] = "abc" * value
    return return_value

  @classmethod
  def setUpTestData(cls):
    cls.fields = {"name": 255}

  def setUp(self):
    self.objects = list()

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()

  def testAddItem(self):
    test_name = "Custard"
    _ = self.sample_item(test_name)

    query = ItemList.objects.filter(name=test_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, test_name)

  def testStr(self):
    test_name = "Beer"
    item = self.sample_item(test_name)

    self.assertEqual(test_name, str(item))

  def testFieldLengths(self):
    with self.assertRaises(DataError):
      _ = self.sample_item(self.generate_overload(self.fields))
