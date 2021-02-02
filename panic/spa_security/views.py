"""Security App Views"""

from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView


class CSRFView(APIView):

  def get(self, request):
    """Returns a 200, and a message containing the CSRF Token."""
    token = get_token(request)
    return Response({"token": token}, status=status.HTTP_200_OK)


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
def csrf_error(request, reason=""):  # pylint: disable=W0613
  """Returns a 403, and a custom error message."""
  return Response(
      {"error": "Refresh csrf and try again."},
      status=status.HTTP_403_FORBIDDEN,
  )
