"""Kitchen custom exception classes."""

from rest_framework import exceptions, serializers, status


class ValidationPermissionError(serializers.ValidationError):
  """Validation exception due to permission problems."""

  default_code = "permission_denied"
  status_code = status.HTTP_403_FORBIDDEN


class ProcessingError(exceptions.APIException):
  """Exception due to processing problems."""

  default_detail = 'An error occurred during processing.'
  default_code = 'processing_error'


class ConfirmationRequired(BaseException):
  """Exception raised when a sensitive operation requires confirmation."""


CUSTOM_VALIDATION_CLASSES = (ValidationPermissionError,)
