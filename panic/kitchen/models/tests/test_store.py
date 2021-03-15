"""Test the Store model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_store import StoreTestHarness
from ..store import Store


class TestStore(ModelTestMixin, StoreTestHarness):
  """Test the Store model."""

  @classmethod
  def create_data_hook(cls):
    cls.fields = {"name": 255}
    cls.create_data = {"user": cls.user1, "name": "Loblaws"}

  def test_create(self):
    test_name = "Loblaws"
    created = self.create_test_instance(user=self.user1, name=test_name)

    query = Store.objects.filter(name=test_name)

    self.assertQuerysetEqual(query, map(repr, [created]))
    # pylint: disable=protected-access
    self.assertEqual(query[0]._index, test_name.lower())

  def test_unique(self):
    test_name = "Loblaws"
    _ = self.create_test_instance(user=self.user1, name=test_name)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(user=self.user1, name=test_name.lower())

    count = Store.objects.filter(name__iexact=test_name).count()
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
