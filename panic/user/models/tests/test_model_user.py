"""Test Custom User Fields"""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..user import CUSTOM_USER_MODEL_FIELDS, User


class TestCustomUserModelFields(TestCase):

  def setUp(self):
    self.data = {
        'username': 'user1',
        'password': 'secret',
        'email': 'user@email.com',
    }

    self.user1 = None

  def tearDown(self):
    if self.user1 and self.user1.id:
      self.user1.delete()

  def test_implements_all_custom_fields(self):
    for field in CUSTOM_USER_MODEL_FIELDS:
      assert getattr(User, field, False)

  def test_language_code_valid(self):
    data = dict(self.data)
    data.update({'language_code': 'en-us'})
    self.user1 = User(**data)
    self.user1.save()

  def test_language_code_invalid(self):
    language = "invalid language"

    data = dict(self.data)
    data.update({'language_code': language})
    self.user1 = User(**data)

    with self.assertRaises(ValidationError) as raised:
      self.user1.save()

    self.assertEqual(
        raised.exception.messages, [f"Invalid language_code '{language}'"]
    )

  def test_timezone_valid(self):
    data = dict(self.data)
    data.update({'timezone': 'Pacific/Fiji'})
    self.user1 = User(**data)
    self.user1.save()

  def test_timezone_invalid(self):
    timezone = "invalid timezone"

    data = dict(self.data)
    data.update({'timezone': timezone})
    self.user1 = User(**data)

    with self.assertRaises(ValidationError) as raised:
      self.user1.save()

    self.assertEqual(
        raised.exception.messages, [f"Invalid timezone '{timezone}'"]
    )

  def test_has_profile_initialized_defaults_to_false(self):
    self.user1 = User(**self.data)
    self.user1.save()

    self.assertFalse(self.user1.has_profile_initialized)

  def test_has_profile_initialized_can_be_set_to_true(self):
    data = dict(self.data)
    data.update({'has_profile_initialized': True})
    self.user1 = User(**data)
    self.user1.save()

    self.assertTrue(self.user1.has_profile_initialized)
