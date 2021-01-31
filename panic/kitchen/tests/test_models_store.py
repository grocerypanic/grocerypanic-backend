"""Test the Store Model."""

from django.core.exceptions import ValidationError

from ..models.store import Store
from .fixtures.store import StoreTestHarness


class TestStore(StoreTestHarness):

  @classmethod
  def create_data_hook(cls):
    cls.fields = {"name": 255}

  @staticmethod
  def generate_overload(fields):
    return_value = []
    for key, value in fields.items():
      return_value.append({key: "abc" * value})
    return return_value

  def testAddStore(self):
    test_name = "Loblaws"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    query = Store.objects.filter(name=test_name)

    assert len(query) == 1
    self.assertEqual(query[0].index, test_name.lower())
    self.assertEqual(query[0].name, test_name)
    self.assertEqual(query[0].user.id, self.user1.id)

  def testUnique(self):
    test_name = "Loblaws"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(user=self.user1, name=test_name)

    count = Store.objects.filter(name=test_name).count()
    assert count == 1

  def testAddStoreInjection(self):
    test_name = "Loblaws<script>alert('hi');</script>"
    sanitized_name = "Loblaws&lt;script&gt;alert('hi');&lt;/script&gt;"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    query = Store.objects.filter(name=sanitized_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, sanitized_name)
    self.assertEqual(query[0].user.id, self.user1.id)

  def testStr(self):
    test_name = "Shoppers Drugmart"
    item = self.create_test_instance(user=self.user1, name=test_name)

    self.assertEqual(test_name, str(item))

  def testFieldLengths(self):
    for overloaded_field in self.generate_overload(self.fields):
      local_data = {"user": self.user1, "name": "Loblaws"}
      local_data.update(overloaded_field)
      with self.assertRaises(ValidationError):
        _ = self.create_test_instance(**local_data)
