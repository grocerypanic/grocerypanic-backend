"""Test the exceptions for the kitchen app."""

from django.test import TestCase
from rest_framework import serializers, status

from .. import (
    ConfirmationRequired,
    ProcessingError,
    ResourceIsRequired,
    ValidationPermissionError,
)


class TestCustomExceptions(TestCase):
  """Test the exceptions for the kitchen app."""

  def test_confirmation_required(self):
    with self.assertRaises(ConfirmationRequired):
      raise ConfirmationRequired()

  def test_processing_error(self):
    with self.assertRaises(ProcessingError) as raised:
      raise ProcessingError()

    self.assertEqual(
        raised.exception.detail,
        serializers.ErrorDetail(
            string=ProcessingError.default_detail,
            code=ProcessingError.default_code
        )
    )

    assert ProcessingError.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

  def test_resource_is_required(self):
    with self.assertRaises(ResourceIsRequired) as raised:
      raise ResourceIsRequired

    self.assertEqual(
        raised.exception.detail,
        serializers.ErrorDetail(
            string=ResourceIsRequired.default_detail,
            code=ResourceIsRequired.default_code
        )
    )

    assert ResourceIsRequired.status_code == status.HTTP_409_CONFLICT

  def test_validation_permission_error(self):
    with self.assertRaises(ValidationPermissionError) as raised:
      raise ValidationPermissionError()

    self.assertListEqual(
        raised.exception.detail, [
            serializers.ErrorDetail(
                string=ValidationPermissionError.default_detail,
                code=ValidationPermissionError.default_code
            )
        ]
    )

    assert ValidationPermissionError.status_code == status.HTTP_403_FORBIDDEN
