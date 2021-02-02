"""Tools for Deprecating API Endpoints"""

from rest_framework import status
from rest_framework.response import Response

DEPRECATED_WARNING = '299 - Planned Deprecation'


def deprecated_warning(response, sunset):
  """Sets deprecation warning headers on a response.

  :param response: A rest framework response object
  :type response: :class:`rest_framework.response.Response`
  :param sunset: A datetime object indicating deprecation date
  :type sunset: :class:`datetime.datetime`

  :returns: A response object with updated headers
  :rtype: :class:`rest_framework.response.Response`
  """
  response['Deprecation'] = sunset
  response['Warning'] = DEPRECATED_WARNING
  response['Sunset'] = sunset
  return response


def deprecated_response(message):
  """Returns a deprecation error.

  :param message: The message content to return
  :type message: str

  :returns: A response object with updated headers
  :rtype: :class:`rest_framework.response.Response`
  """
  return Response({"detail": message}, status=status.HTTP_410_GONE)
