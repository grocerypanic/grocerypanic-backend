"""Custom Item Quantity Validators"""

from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from ..item import MAXIMUM_QUANTITY, MINIMUM_QUANTITY


@deconstructible
class TransactionQuantityValidator(BaseValidator):
  """Enforce a upper and lower bounds, and require the value not be zero."""

  message = _(
      'This value must be non-zero integer between '
      '-%(limit_value)s and %(limit_value)s.'
  )
  code = 'invalid_quantity'

  def compare(self, a, b):
    return abs(a) >= abs(b) or a == 0


def related_item_quantity_validator(value):
  """Performs validation of a the related item's quantity field.
  This validator produces a more useful error message for end users.

  :param value: The quantity to be validated
  :type value: float
  :returns: The validated value
  :rtype: value
  :raises: :class:`django.core.exceptions.ValidationError`
  """
  if value < MINIMUM_QUANTITY or value >= MAXIMUM_QUANTITY:
    raise ValidationError({
        'item': [
            "This object's 'quantity' may not reduced below"
            f" {MINIMUM_QUANTITY}, or above {MAXIMUM_QUANTITY}."
        ],
    })
  return value
