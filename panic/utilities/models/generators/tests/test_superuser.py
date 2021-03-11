"""Test the create_superuser function."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..superuser import ERROR_MESSAGE, create_superuser

User = get_user_model()


class TestCreateUser(TestCase):
  """Test the create_superuser function."""

  def _call_function(self, **kwargs):
    result = create_superuser(**kwargs)
    if result:
      self.objects.append(result)
    return result

  def setUp(self):
    self.objects = []

  def test_create_defaults(self):
    user = self._call_function()

    assert user.username == "admin"
    assert user.email == "test@example.com"
    assert user.check_password("admin")

  def test_create_default_twice(self):
    self._call_function()

    with self.assertRaises(Exception) as raised:
      self._call_function()

    self.assertEqual(
        raised.exception.args[0],
        ERROR_MESSAGE,
    )

  def test_create_specified(self):
    test_username = "superuser"
    test_password = "superuser"

    user = self._call_function(username=test_username, password=test_password)

    assert user.username == test_username
    assert user.email == "test@example.com"
    assert user.check_password(test_password)

  def tearDown(self):
    for obj in self.objects:
      obj.delete()
