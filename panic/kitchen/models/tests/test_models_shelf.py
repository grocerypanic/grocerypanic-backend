"""Test the Shelf model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_shelf import ShelfTestHarness
from ..shelf import Shelf


class TestShelf(ModelTestMixin, ShelfTestHarness):
  """Test the Shelf model."""

  @classmethod
  def create_data_hook(cls):
    cls.fields = {"name": 255}
    cls.create_data = {"user": cls.user1, "name": "Refrigerator"}

  def test_create(self):
    test_name = "Refrigerator"
    shelf = self.create_test_instance(user=self.user1, name=test_name)
    query = Shelf.objects.filter(name=test_name)

    self.assertQuerysetEqual(query, [repr(shelf)])
    self.assertEqual(query[0].index, self.create_data['name'].lower())

  def test_unique(self):
    test_name = "Above Sink"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(user=self.user1, name=test_name)

    count = Shelf.objects.filter(name=test_name).count()
    assert count == 1

  def test_bleach(self):
    test_name = "Refrigerator<script>alert('hi');</script>"
    sanitized_name = "Refrigerator&lt;script&gt;alert('hi');&lt;/script&gt;"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    query = Shelf.objects.filter(name=sanitized_name)

    assert len(query) == 1
    self.assertEqual(query[0].index, sanitized_name.lower())
    self.assertEqual(query[0].name, sanitized_name)
    self.assertEqual(query[0].user.id, self.user1.id)

  def test_str(self):
    test_name = "Pantry"
    item = self.create_test_instance(user=self.user1, name=test_name)

    self.assertEqual(test_name, str(item))
