"""Test the custom exception handler."""

from django.test import TestCase
from rest_framework import serializers, status

from .. import ProcessingError, ValidationPermissionError


class TestCustomExceptions(TestCase):
  """Test the custom exceptions."""

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
