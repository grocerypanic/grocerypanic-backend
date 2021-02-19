"""Custom User Serializer Validators"""

from langcodes import Language
from langcodes.tag_parser import LanguageTagError
from rest_framework import serializers


def validate_language(value):
  """Validates a given language code.

  :param value: A string containing a language code.
  :type value: str
  :raises: :class:`django.core.exceptions.ValidationError`
  """
  try:
    Language.get(value).is_valid()
  except LanguageTagError:
    raise serializers.ValidationError(f"Invalid language_code '{value}'",)
