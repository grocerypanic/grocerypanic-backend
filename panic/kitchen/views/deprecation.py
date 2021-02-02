"""Tools for Deprecating API Endpoints"""

from rest_framework import status
from rest_framework.response import Response

DEPRECATED_WARNING = '299 - Planned Deprecation'


def deprecated_warning(response, sunset):
  response['Deprecation'] = sunset
  response['Warning'] = DEPRECATED_WARNING
  response['Sunset'] = sunset
  return response


def deprecated_response(message):
  return Response({"detail": message}, status=status.HTTP_410_GONE)
