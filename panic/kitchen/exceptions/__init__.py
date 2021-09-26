"""Exception classes for the kitchen app."""

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


class ResourceIsRequired(exceptions.APIException):
  """Exception due to related dependency."""

  default_detail = "This resource is required by another object."
  status_code = status.HTTP_409_CONFLICT


CUSTOM_VALIDATION_CLASSES = (ValidationPermissionError,)
