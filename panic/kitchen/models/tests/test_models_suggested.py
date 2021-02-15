"""Test the SuggestedItem model."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..suggested import SuggestedItem
from .fixtures.fixture_models import generate_base


class TestItemList(generate_base(TestCase)):
  """Test the SuggestedItem model."""

  def create_test_instance(self, name="Red Beans"):
    """Create a test suggested item."""
    item = SuggestedItem.objects.create(name=name)
    self.objects.append(item)
    return item

  @classmethod
  def setUpTestData(cls):
    cls.fields = {"name": 255}
    cls.data = {"name": "Ice Cream"}

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def test_create(self):
    test_name = "Custard"
    _ = self.create_test_instance(test_name)

    query = SuggestedItem.objects.filter(name=test_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, test_name)

  def test_unique(self):
    test_name = "Custard"
    _ = self.create_test_instance(test_name)

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(test_name)

    query = SuggestedItem.objects.filter(name=test_name)
    assert len(query) == 1

  def test_bleach(self):
    test_name = "Broccoli<script>alert('hi');</script>"
    sanitized_name = "Broccoli&lt;script&gt;alert('hi');&lt;/script&gt;"

    _ = self.create_test_instance(test_name)

    query = SuggestedItem.objects.filter(name=sanitized_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, sanitized_name)

  def test_str(self):
    test_name = "Beer"
    item = self.create_test_instance(test_name)

    self.assertEqual(test_name, str(item))
