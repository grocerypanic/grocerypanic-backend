"""CSRF error view returning a JSON response."""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

CSRF_ERROR_MESSAGE = "Refresh csrf and try again."


@api_view([
    'CONNECT',
    'DELETE',
    'GET',
    'HEAD',
    'OPTIONS',
    'POST',
    'PATCH',
    'PUT',
    'TRACE',
])
def csrf_error_view(request, reason=""):  # pylint: disable=unused-argument
  """Respond to CSRF error with a 403, and a custom JSON message."""

  return Response(
      {"error": CSRF_ERROR_MESSAGE},
      status=status.HTTP_403_FORBIDDEN,
  )
