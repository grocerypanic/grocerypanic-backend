"""Test the Custom Exception Handler"""

from unittest.mock import patch

from django.test import TestCase
from rest_framework import serializers, status
from rest_framework.response import Response

from .. import exceptions
from ..exceptions import (
    CustomValidationExceptionHandler,
    ProcessingError,
    ValidationPermissionError,
    kitchen_exception_handler,
)


class TestCustomExceptions(TestCase):

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


class ExceptionTestHarness(TestCase):

  def setUp(self):
    self.validation_error = 'a validation error message'
    self.field_error = {'field': [self.validation_error]}
    self.data = {'detail': self.field_error}
    self.status = status.HTTP_200_OK

    self.response = Response(data=self.data, status=self.status)
    self.base_exception = BaseException(self.validation_error)
    self.validation_exception = serializers.ValidationError(
        detail=self.validation_error,
    )


class TestCustomExceptionHandler(ExceptionTestHarness):

  @patch(exceptions.__name__ + '.views.exception_handler')
  def test_regular_exception(self, mock_handler):
    mock_handler.return_value = self.response
    response = kitchen_exception_handler(self.base_exception, {})

    self.assertEqual(response.status_code, self.response.status_code)

  @patch(exceptions.__name__ + '.views.exception_handler')
  def test_regular_exception_none(self, mock_handler):
    mock_handler.return_value = None
    response = kitchen_exception_handler(self.base_exception, {})

    self.assertIsNone(response)

  @patch(exceptions.__name__ + '.views.exception_handler')
  def test_custom_validation_exception(self, mock_handler):
    custom_exception = ValidationPermissionError(detail=self.field_error,)

    mock_handler.return_value = self.response
    response = kitchen_exception_handler(custom_exception, {})

    self.assertEqual(
        response.status_code, ValidationPermissionError.status_code
    )


class TestCustomValidationExceptionHandler(ExceptionTestHarness):

  def testBaseExceptionNotFormatted(self):
    handler = CustomValidationExceptionHandler(
        self.base_exception,
        self.response,
    )
    handler.process()

    self.assertEqual(handler.response.status_code, self.status)

  def testValidationExceptionNotFormatted(self):
    handler = CustomValidationExceptionHandler(
        self.validation_exception,
        self.response,
    )
    handler.process()

    self.assertEqual(handler.response.status_code, self.status)

  def testValidationExceptionFormatted(self):
    handler = CustomValidationExceptionHandler(
        serializers.ValidationError(detail=self.field_error,),
        self.response,
    )
    handler.process()

    self.assertEqual(handler.response.status_code, self.status)

  def testCustomExceptionCorrectStatus(self):
    handler = CustomValidationExceptionHandler(
        ValidationPermissionError(detail=self.field_error,),
        self.response,
    )
    handler.process()

    self.assertNotEqual(handler.response.status_code, self.status)

    self.assertEqual(
        handler.response.status_code, ValidationPermissionError.status_code
    )

  def testCustomExceptionIncorrectStatus(self):
    handler = CustomValidationExceptionHandler(
        ValidationPermissionError(
            detail=self.field_error,
            code="some_other_reason",
        ),
        self.response,
    )
    handler.process()

    self.assertEqual(handler.response.status_code, self.status)
