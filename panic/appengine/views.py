"""Views for the appengine app."""

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from rest_framework import status

from utilities.config.module_cache import warm_module_cache
from utilities.database.connection import wait_for_database_connection


class WarmUp(View):
  """Handle App Engine `warm up` requests.

  App Engine `warm up` documentation::
    - https://cloud.google.com/appengine/docs/standard/python3/\
configuring-warmup-requests
  """

  def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
    """Process an App Engine `warm up` request."""

    wait_for_database_connection(settings.WARM_UP_DATABASE_WAIT_INTERVAL)
    warm_module_cache()

    return HttpResponse('OK', status=status.HTTP_200_OK)
