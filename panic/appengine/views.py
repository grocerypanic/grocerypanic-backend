"""Views for the appengine app."""

from importlib import import_module

from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from rest_framework import status

from utilities.database.connection import wait_for_database_connection

DATABASE_WAIT_INTERVAL = 0.5


class WarmUp(View):
  """Handle Requests Related to App Engine's 'warm up' feature.

  `App Engine Warm Up Documentation
  <https://cloud.google.com/appengine/docs/standard/python3/
  configuring-warmup-requests>`__
  """

  def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
    """Process an App Engine Warmup Request."""

    wait_for_database_connection(DATABASE_WAIT_INTERVAL)
    self._import_installed_apps()

    return HttpResponse('OK', status=status.HTTP_200_OK)

  @staticmethod
  def _import_installed_apps():
    for app in settings.INSTALLED_APPS:
      for name in ('urls', 'views', 'models'):
        try:
          import_module('%s.%s' % (app, name))
        except ImportError:
          pass
