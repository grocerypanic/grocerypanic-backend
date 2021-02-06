"""Custom Item Quantity Validators"""

from django.core.exceptions import ValidationError


def validate_transaction_quantity(value):
  """Validator for Transaction Quantity.

  :param value: The quantity to be validated
  :type value: float

  :returns: The validated value
  :rtype: value
  :raises: :class:`django.core.exceptions.ValidationError`
  """
  if value == 0:
    raise ValidationError([{'quantity': "Must not be equal to 0"}])
  return value
