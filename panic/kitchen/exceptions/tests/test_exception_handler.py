"""Test the custom exception handler."""

from unittest.mock import patch

from rest_framework import serializers

from .. import ValidationPermissionError, handler
from .fixtures.fixtures_handler import HandlerTestHarness


class TestCustomExceptionHandler(HandlerTestHarness):
  """Test the custom exception handler."""

  __test__ = True

  @patch(handler.__name__ + '.views.exception_handler')
  def test_regular_exception(self, mock_handler):
    mock_handler.return_value = self.response
    response = handler.exception_handler(self.base_exception, {})

    self.assertEqual(response.status_code, self.response.status_code)

  @patch(handler.__name__ + '.views.exception_handler')
  def test_regular_exception_none(self, mock_handler):
    mock_handler.return_value = None
    response = handler.exception_handler(self.base_exception, {})

    self.assertIsNone(response)

  @patch(handler.__name__ + '.views.exception_handler')
  def test_custom_validation_exception(self, mock_handler):
    custom_exception = ValidationPermissionError(detail=self.field_error,)

    mock_handler.return_value = self.response
    response = handler.exception_handler(custom_exception, {})

    self.assertEqual(
        response.status_code, ValidationPermissionError.status_code
    )


class TestCustomValidationExceptionHandler(HandlerTestHarness):
  """Test the custom validation exception handler."""

  __test__ = True

  def test_base_exception_not_formatted(self):
    custom_exception_handler = handler.CustomValidationExceptionHandler(
        self.base_exception,
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(
        custom_exception_handler.response.status_code,
        self.status,
    )

  def test_validation_exception_not_formatted(self):
    custom_exception_handler = handler.CustomValidationExceptionHandler(
        self.validation_exception,
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(custom_exception_handler.response.status_code, self.status)

  def test_validation_exception_formatted(self):
    custom_exception_handler = handler.CustomValidationExceptionHandler(
        serializers.ValidationError(detail=self.field_error,),
        self.response,
    )
    custom_exception_handler.process()

    self.assertEqual(
        custom_exception_handler.response.status_code,
        self.status,
    )

  def test_custom_exception_correct_status(self):
    custom_exception_handler = handler.CustomValidationExceptionHandler(
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
    custom_exception_handler = handler.CustomValidationExceptionHandler(
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
