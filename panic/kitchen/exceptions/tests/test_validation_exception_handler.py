"""Test the custom exception handler."""

from rest_framework import serializers

from root.tests.fixtures.fixtures_exception_handler import HandlerTestHarness
from .. import ValidationPermissionError
from ..validation_exception_handler import ValidationExceptionHandler


class TestCustomValidationExceptionHandler(HandlerTestHarness):
  """Test the custom validation exception handler."""

  def test_base_exception_not_formatted(self):
    custom_exception_handler = ValidationExceptionHandler(
        self.base_exception,
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(
        custom_exception_handler.response.status_code,
        self.status,
    )

  def test_validation_exception_not_formatted(self):
    custom_exception_handler = ValidationExceptionHandler(
        self.validation_exception,
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(custom_exception_handler.response.status_code, self.status)

  def test_validation_exception_formatted(self):
    custom_exception_handler = ValidationExceptionHandler(
        serializers.ValidationError(detail=self.field_error,),
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(
        custom_exception_handler.response.status_code,
        self.status,
    )

  def test_custom_exception_correct_status(self):
    custom_exception_handler = ValidationExceptionHandler(
        ValidationPermissionError(detail=self.field_error,),
        self.response,
    )
    custom_exception_handler.process()

    self.assertNotEqual(
        custom_exception_handler.response.status_code,
        self.status,
    )

    self.assertEqual(
        custom_exception_handler.response.status_code,
        ValidationPermissionError.status_code,
    )

  def test_custom_exception_incorrect_status(self):
    custom_exception_handler = ValidationExceptionHandler(
        ValidationPermissionError(
            detail=self.field_error,
            code="some_other_reason",
        ),
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(
        custom_exception_handler.response.status_code,
        self.status,
    )
