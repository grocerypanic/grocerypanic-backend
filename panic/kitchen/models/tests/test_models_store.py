"""Test the Store model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixtures_store import StoreTestHarness
from ..store import Store
from .fixtures.fixture_models import generate_base


class TestStore(generate_base(StoreTestHarness)):
  """Test the Store model."""

  @classmethod
  def create_data_hook(cls):
    cls.fields = {"name": 255}
    cls.data = {"user": cls.user1, "name": "Loblaws"}

  def test_create(self):
    test_name = "Loblaws"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    query = Store.objects.filter(name=test_name)

    assert len(query) == 1
    self.assertEqual(query[0].index, test_name.lower())
    self.assertEqual(query[0].name, test_name)
    self.assertEqual(query[0].user.id, self.user1.id)

  def test_unique(self):
    test_name = "Loblaws"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(user=self.user1, name=test_name)

    count = Store.objects.filter(name=test_name).count()
    assert count == 1

  def test_bleach(self):
    test_name = "Loblaws<script>alert('hi');</script>"
    sanitized_name = "Loblaws&lt;script&gt;alert('hi');&lt;/script&gt;"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    query = Store.objects.filter(name=sanitized_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, sanitized_name)
    self.assertEqual(query[0].user.id, self.user1.id)

  def test_str(self):
    test_name = "Shoppers Drugmart"
    item = self.create_test_instance(user=self.user1, name=test_name)

    self.assertEqual(test_name, str(item))
