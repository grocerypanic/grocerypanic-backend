"""Test fixtures for exception handlers."""

from django.test import SimpleTestCase
from rest_framework import serializers, status
from rest_framework.response import Response


class HandlerTestHarness(SimpleTestCase):
  """Test harness for the exception handlers."""

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
