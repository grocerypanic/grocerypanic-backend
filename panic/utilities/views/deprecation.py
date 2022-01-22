"""Tools for deprecating API endpoints."""

from datetime import date, datetime
from typing import Union

from rest_framework import status
from rest_framework.response import Response

DEPRECATED_WARNING = '299 - Planned Deprecation'


def deprecated_warning(
    response: Response, sunset: Union[datetime, date]
) -> Response:
  """Set deprecation warning headers on a response.

  :param response: A rest framework response object
  :type response: :class:`rest_framework.response.Response`
  :param sunset: A datetime or data object indicating deprecation date
  :type sunset: Union[datetime, date]

  :returns: A response object with updated headers
  :rtype: :class:`rest_framework.response.Response`
  """
  response['Deprecation'] = str(sunset)
  response['Warning'] = DEPRECATED_WARNING
  response['Sunset'] = str(sunset)
  return response


def deprecated_response(message: str) -> Response:
  """Return a deprecation error.

  :param message: The message content to return
  :type message: str

  :returns: A response object with updated headers
  :rtype: :class:`rest_framework.response.Response`
  """
  return Response({"detail": message}, status=status.HTTP_410_GONE)
