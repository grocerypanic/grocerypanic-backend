"""Test the SuggestedItem model."""

from django.core.exceptions import ValidationError

from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_suggested import SuggestedItemTestHarness
from ..suggested import SuggestedItem


class TestItemList(ModelTestMixin, SuggestedItemTestHarness):
  """Test the SuggestedItem model."""

  @classmethod
  def create_data_hook(cls):
    cls.fields = {"name": 255}
    cls.create_data = {"name": "Ice Cream"}
    cls.test_item_name = "Red Beans"

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def test_create(self):
    item = self.create_test_instance(name=self.test_item_name)

    query = SuggestedItem.objects.filter(name=self.test_item_name)

    self.assertQuerysetEqual(query, [repr(item)])

  def test_unique(self):
    _ = self.create_test_instance(name=self.test_item_name)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(name=self.test_item_name)

    query = SuggestedItem.objects.filter(name=self.test_item_name)
    assert len(query) == 1

  def test_bleach(self):
    dangerous_test_name = "Broccoli<script>alert('hi');</script>"
    sanitized_name = "Broccoli&lt;script&gt;alert('hi');&lt;/script&gt;"

    _ = self.create_test_instance(name=dangerous_test_name)

    query = SuggestedItem.objects.filter(name=sanitized_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, sanitized_name)

  def test_str(self):
    item = self.create_test_instance(name=self.test_item_name)

    self.assertEqual(self.test_item_name, str(item))
