"""Test the create_superuser function."""

from typing import Any, List

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase

from ..superuser import ERROR_MESSAGE, create_superuser

User = get_user_model()


class TestCreateUser(TestCase):
  """Test the create_superuser function."""

  def _call_function(self, **kwargs: Any) -> Model:
    result = create_superuser(**kwargs)
    if result:
      self.objects.append(result)
    return result

  def setUp(self) -> None:
    self.objects: List[Model] = []

  def test_create_defaults(self) -> None:
    user = self._call_function()

    assert user.username == "admin"  # type: ignore
    assert user.email == "test@example.com"  # type: ignore
    assert user.check_password("admin")  # type: ignore

  def test_create_default_twice(self) -> None:
    self._call_function()

    with self.assertRaises(Exception) as raised:
      self._call_function()

    self.assertEqual(
        raised.exception.args[0],
        ERROR_MESSAGE,
    )

  def test_create_specified(self) -> None:
    test_username = "superuser"
    test_password = "superuser"

    user = self._call_function(username=test_username, password=test_password)

    assert user.username == test_username  # type: ignore
    assert user.email == "test@example.com"  # type: ignore
    assert user.check_password(test_password)  # type: ignore

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()
