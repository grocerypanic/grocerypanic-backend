"""Test Custom User Serializer Validators"""

from django.test import TestCase
from rest_framework import serializers

from ..user import validate_language


class TestUserModel(TestCase):

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
