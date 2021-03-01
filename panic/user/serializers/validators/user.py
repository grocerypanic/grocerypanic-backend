"""Custom user serializer validators."""

from langcodes import Language
from langcodes.tag_parser import LanguageTagError
from rest_framework import serializers


def validate_language(value):
  """Validate a given language code.

  :param value: A string containing a language code.
  :type value: str
  :raises: :class:`django.core.exceptions.ValidationError`
  """
  try:
    Language.get(value).is_valid()
  except LanguageTagError:
    # pylint: disable=raise-missing-from
    raise serializers.ValidationError(f"Invalid language_code '{value}'",)
