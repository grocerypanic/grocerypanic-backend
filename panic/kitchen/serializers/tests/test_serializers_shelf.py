"""Test the Shelf serializer."""

from rest_framework.serializers import ValidationError

from ...models.shelf import Shelf
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_shelf import ShelfTestHarness
from .. import DUPLICATE_OBJECT_MESSAGE
from ..shelf import ShelfSerializer
from .fixtures.fixtures_serializers import generate_base


class TestShelf(generate_base(ShelfTestHarness)):
  """Test the Shelf serializer."""

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ShelfSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)
    cls.data = {"name": "Pantry"}

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def test_deserialize(self):
    test_value = "Refrigerator"

    shelf = self.create_test_instance(user=self.user1, name=test_value)
    serialized = self.serializer(shelf)

    self.assertEqual(serialized.data['name'], test_value)

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    self.assertEqual(serialized.data['name'], self.data['name'])

    query = Shelf.objects.filter(name="Pantry")

    assert len(query) == 1
    self.assertEqual(query[0].user.id, self.user1.id)
    self.assertEqual(query[0].name, "Pantry")

  def test_unique_constraint(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        data=self.data,
    )
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['non_field_errors'][0]), DUPLICATE_OBJECT_MESSAGE
    )
