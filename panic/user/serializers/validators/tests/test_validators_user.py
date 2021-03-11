"""Test User model serializer validators."""

from django.test import SimpleTestCase
from rest_framework import serializers

from ..user import validate_language


class TestUserModel(SimpleTestCase):
  """Test the validate_language function."""

  def setUp(self):
    self.data = {
        'username': 'user1',
        'password': 'secret',
        'email': 'user@email.com',
    }

  def test_language_code_valid(self):
    validate_language('en-us')

  def test_language_code_invalid(self):
    language = "invalid language"

    with self.assertRaises(serializers.ValidationError) as raised:
      validate_language(language)

    self.assertEqual(
        raised.exception.detail, [f"Invalid language_code '{language}'"]
    )
