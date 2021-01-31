"""Test the Shelf Serializer."""

from rest_framework.serializers import ValidationError

from ..models.shelf import Shelf
from ..serializers import DUPLICATE_OBJECT_MESSAGE
from ..serializers.shelf import ShelfSerializer
from .fixtures.django import MockRequest
from .fixtures.shelf import ShelfTestHarness


class TestShelf(ShelfTestHarness):

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ShelfSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)

  @staticmethod
  def generate_overload(fields):
    return_list = []
    for key, value in fields.items():
      overloaded = dict()
      overloaded[key] = "abc" * value
      return_list.append(overloaded)
    return return_list

  def setUp(self):
    self.objects = list()

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()

  def testDeserialize(self):
    test_value = "Refrigerator"

    shelf = self.create_test_instance(user=self.user1, name=test_value)
    serialized = self.serializer(shelf)

    self.assertEqual(serialized.data['name'], test_value)

  def testSerialize(self):
    test_value = {"name": "Pantry"}

    serialized = self.serializer(
        context={'request': self.request},
        data=test_value,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    self.assertEqual(serialized.data['name'], test_value['name'])

    query = Shelf.objects.filter(name="Pantry")

    assert len(query) == 1
    self.assertEqual(query[0].user.id, self.user1.id)
    self.assertEqual(query[0].name, "Pantry")

  def testUniqueConstraint(self):
    test_value = {"name": "Pantry"}

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

  def testFieldLengths(self):
    overloads = self.generate_overload(self.fields)
    for overload in overloads:
      with self.assertRaises(ValidationError):
        serialized = self.serializer(
            context={'request': self.request},
            data=overload,
        )
        serialized.is_valid(raise_exception=True)
