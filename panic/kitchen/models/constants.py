"""Shared model constants."""

from decimal import Decimal

TWO_PLACES = Decimal(10)**-2
MAXIMUM_QUANTITY = 10000
MINIMUM_QUANTITY = 0

UNIQUE_NAME_CONSTRAINT_ERROR = {
    'name': 'This field must be unique for each user.'
}
