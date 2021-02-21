"""Test the Store serializer."""

from rest_framework.serializers import ValidationError

from ...models.store import Store
from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest
from ...tests.fixtures.fixtures_store import StoreTestHarness
from .. import DUPLICATE_OBJECT_MESSAGE
from ..store import StoreSerializer


class TestStore(SerializerTestMixin, StoreTestHarness):
  """Test the Store serializer."""

  @classmethod
  def create_data_hook(cls):
    cls.serializer = StoreSerializer
    cls.fields = {"name": 255}
    cls.create_data = {"name": "Super Store"}
    cls.request = MockRequest(cls.user1)

  def test_deserialize(self):
    test_value = "Loblaws"
    store = self.create_test_instance(user=self.user1, name=test_value)

    serialized = self.serializer(store)
    self.assertEqual(serialized.data['name'], test_value)

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.create_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    self.assertEqual(serialized.data['name'], self.create_data['name'])

    query = Store.objects.filter(name=self.create_data['name'])

    assert len(query) == 1
    self.assertEqual(query[0].user.id, self.user1.id)
    self.assertEqual(query[0].name, self.create_data['name'])

  def test_unique_constraint(self):
    test_value = {"name": "Super Store"}

    serialized = self.serializer(
        context={'request': self.request},
        data=test_value,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        data=test_value,
    )
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['non_field_errors'][0]), DUPLICATE_OBJECT_MESSAGE
    )
