"""Custom user model validators."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from langcodes import Language
from langcodes.tag_parser import LanguageTagError


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
    raise ValidationError(
        _("Invalid language_code '%(value)s'"),
        params={'value': value},
    )
