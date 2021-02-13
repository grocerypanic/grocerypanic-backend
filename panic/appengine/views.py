"""Views for the appengine app."""

from django.http import HttpResponse
from django.views.generic import View


class WarmUp(View):
  """Handle Requests Related to App Engine's 'warm up' feature.

  `App Engine Warm Up Documentation
  <https://cloud.google.com/appengine/docs/standard/python3/
  configuring-warmup-requests>`__
  """

  def get(self, request, *args, **kwargs):  # pylint: disable=W0613
    """Process an App Engine Warmup Request."""

    return HttpResponse('OK', status=200)
