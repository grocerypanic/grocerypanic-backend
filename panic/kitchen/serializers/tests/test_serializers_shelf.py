"""Test the Shelf serializer."""

from rest_framework.serializers import ValidationError

from ...models.shelf import Shelf
from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_shelf import ShelfTestHarness
from .. import UNIQUE_CONSTRAINT_MSG
from ..shelf import ShelfSerializer


class TestShelf(SerializerTestMixin, ShelfTestHarness):
  """Test the Shelf serializer."""

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ShelfSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)
    cls.create_data = {"name": "Pantry"}

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
        data=self.create_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    self.assertEqual(serialized.data['name'], self.create_data['name'])

    query = Shelf.objects.filter(name="Pantry")

    assert len(query) == 1
    self.assertEqual(query[0].user.id, self.user1.id)
    self.assertEqual(query[0].name, "Pantry")

  def test_case_unique_constraint(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.create_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    case_change = dict(self.create_data)
    case_change.update({"name": self.create_data['name'].lower()})

    serialized2 = self.serializer(
        context={'request': self.request},
        data=case_change,
    )
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['name'][0]),
        UNIQUE_CONSTRAINT_MSG,
    )

  def test_case_unique_constraint_update_instance(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.create_data,
    )
    serialized.is_valid(raise_exception=True)
    instance = serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        instance=instance,
        data={"name": self.create_data['name'].lower()},
        partial=True
    )

    serialized2.is_valid(raise_exception=True)
    serialized2.save()

    self.assertEqual(
        instance.name,
        self.create_data['name'].lower(),
    )
