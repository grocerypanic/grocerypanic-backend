"""Root exception handler for the kitchen app."""

from rest_framework import views

from .validation_exception_handler import ValidationExceptionHandler


def root_exception_handler(exc, context):
  """Handle exceptions and call other exception handlers as needed.

  :param exc: An exception
  :type exc: :class:`BaseException`
  :param context: A dictionary produced by the API view
  :type context: dict

  :returns: A rest_framework response object
  :rtype: :class:`rest_framework.response.Response`
  """

  response = views.exception_handler(exc, context)

  if response is not None:
    handler = ValidationExceptionHandler(exc, response)
    handler.process()
    response = handler.response

  return response
