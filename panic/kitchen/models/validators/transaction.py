"""Custom transaction validators."""

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from .. import constants


@deconstructible
class TransactionQuantityValidator(BaseValidator):
  """Enforce a upper and lower bounds, and require the value not be zero."""

  message = _(
      'This value must be non-zero integer between '
      '-%(limit_value)s and %(limit_value)s.'
  )
  code = 'invalid_quantity'

  def compare(self, a, b):
    """Perform the bounds calculation."""
    return abs(a) >= abs(b) or a == 0


def related_item_quantity_validator(value):
  """Perform validation of a the related item's quantity field.
  This validator produces a more useful error message for end users.

  :param value: The quantity to be validated
  :type value: float
  :returns: The validated value
  :rtype: value
  :raises: :class:`django.core.exceptions.ValidationError`
  """
  if value < constants.MINIMUM_QUANTITY or value >= constants.MAXIMUM_QUANTITY:
    raise ValidationError({
        'item': [
            "This object's 'quantity' may not reduced below"
            f" {constants.MINIMUM_QUANTITY}, or above"
            f" {constants.MAXIMUM_QUANTITY}."
        ],
    })
  return value
