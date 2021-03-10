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

  serializer_data: dict
  fields: dict

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ShelfSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)

    cls.calculated_properties = set()
    cls.m2m_fields = set()

    cls.create_data = {
        "name": "Pantry",
        "user": cls.user1,
    }

    cls.serializer_data = {
        "name": "Pantry",
    }

  def test_deserialize(self):
    shelf = self.create_test_instance(**self.create_data)
    serialized = self.serializer(shelf)
    representation = self._instance_to_dict(shelf, exclude=['user'])

    self.assertEqual(serialized.data, representation)

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Shelf.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    shelf = query[0]

    expected = dict(self.serializer_data)
    representation = self._instance_to_dict_subset(shelf, expected)

    self.assertDictEqual(representation, expected)

  def test_serializer_user(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Shelf.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    shelf = query[0]

    self.assertEqual(shelf.user.id, self.user1.id)

  def test_case_unique_constraint(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    case_change = dict(self.serializer_data)
    case_change.update({"name": self.serializer_data['name'].lower()})

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
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    instance = serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        instance=instance,
        data={"name": self.serializer_data['name'].lower()},
        partial=True
    )

    serialized2.is_valid(raise_exception=True)
    serialized2.save()

    self.assertEqual(
        instance.name,
        self.serializer_data['name'].lower(),
    )
