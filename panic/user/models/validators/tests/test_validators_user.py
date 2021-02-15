"""Test custom user model validators."""

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..user import validate_language


class TestValidationLanguage(TestCase):
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

    with self.assertRaises(ValidationError) as raised:
      validate_language(language)

    self.assertEqual(
        raised.exception.messages, [f"Invalid language_code '{language}'"]
    )
