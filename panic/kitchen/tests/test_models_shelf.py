"""Test the Shelf Model."""

from django.contrib.auth import get_user_model
from django.db.utils import DataError
from django.test import TestCase

from ..models.shelf import Shelf


class TestShelf(TestCase):

  def sample_shelf(self, user=None, name="Over Sink"):
    """Create a test user account."""
    if user is None:
      user = self.user
    shelf = Shelf.objects.create(user=user, name=name)
    self.objects.append(shelf)
    return shelf

  @staticmethod
  def generate_overload(fields):
    return_value = {}
    for key, value in fields.items():
      return_value[key] = "abc" * value
    return return_value

  @classmethod
  def setUpTestData(cls):
    cls.fields = {"name": 255}
    cls.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )

  def setUp(self):
    self.objects = list()

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()

  def testAddItem(self):
    test_name = "Refrigerator"
    _ = self.sample_shelf(self.user, test_name)

    query = Shelf.objects.filter(name=test_name)

    assert len(query) == 1
    self.assertEqual(query[0].name, test_name)
    self.assertEqual(query[0].user.id, self.user.id)

  def testStr(self):
    test_name = "Pantry"
    item = self.sample_shelf(self.user, test_name)

    self.assertEqual(test_name, str(item))

  def testFieldLengths(self):
    with self.assertRaises(DataError):
      _ = self.sample_shelf(self.user, self.generate_overload(self.fields))
