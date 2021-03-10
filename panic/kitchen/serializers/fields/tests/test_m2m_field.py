"""Tests for the M2MThroughSerializerField class."""

from ....models.store import Store
from ....tests.fixtures.fixtures_store import StoreTestHarness
from ..m2m import M2MThroughSerializerField


class TestM2MThroughSerializerField(StoreTestHarness):
  """Test the M2MThroughSerializerField class."""

  @classmethod
  def create_data_hook(cls):
    cls.create_data1 = {"name": "Metro", "user": cls.user1}
    cls.store1 = cls.create_instance(**cls.create_data1)

  def setUp(self):
    super().setUp()
    self.field = M2MThroughSerializerField(queryset=Store.objects.all())

  def test_to_internal_int(self):
    result = self.field.to_internal_value(self.store1.id)

    self.assertEqual(
        result,
        self.store1,
    )

  def test_to_internal_str(self):
    result = self.field.to_internal_value(str(self.store1.id))

    self.assertEqual(
        result,
        self.store1,
    )

  def test_to_internal_instance(self):
    result = self.field.to_internal_value(self.store1)

    self.assertEqual(
        result,
        self.store1,
    )

  def test_to_representation(self):
    result = self.field.to_representation(self.store1)

    self.assertEqual(
        result,
        self.store1.id,
    )
