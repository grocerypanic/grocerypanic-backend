"""Validation exception handling for the kitchen app."""

from django.contrib.admin.utils import flatten
from rest_framework import serializers

from . import CUSTOM_VALIDATION_CLASSES


class ValidationExceptionHandler:
  """Handle custom validation errors that are hidden by DRF.

  :param exc: An exception
  :type exc: :class:`rest_framework.serializers.APIException`
  :param response: A rest_framework response object
  :type response: :class:`rest_framework.response.Response`
  """

  def __init__(self, exc, response):
    self.exc = exc
    self.error_message_list = []
    self.response = response

  def process(self):
    """Process an exception, and modify the response if needed."""

    if isinstance(self.exc, serializers.ValidationError):
      self.error_message_list = self.__get_validation_errors()
      self.response = self.__set_status_code()

  def __get_validation_errors(self):
    try:
      return flatten(self.exc.get_full_details().values())
    except AttributeError:
      return []

  def __set_status_code(self):
    for error in self.error_message_list:
      for validator in CUSTOM_VALIDATION_CLASSES:
        if 'code' in error and error['code'] == validator.default_code:
          self.response.status_code = validator.status_code
    return self.response
