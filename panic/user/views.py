"""Views for the user app."""

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers.timezones import TimezoneSerializer
from .utilities.timezones import generate_timezones


class TimeZones(APIView):
  """User Timezones API view."""

  @swagger_auto_schema(
      responses={status.HTTP_200_OK: TimezoneSerializer(many=True)},
  )
  def get(self, request):  # pylint: disable=unused-argument
    """User Timezones API view."""

    serialized = TimezoneSerializer(generate_timezones(), many=True)
    return Response(serialized.data)
