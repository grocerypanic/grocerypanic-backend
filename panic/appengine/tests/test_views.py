"""Test the app engine app views."""

from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve, reverse

from ..views import WarmUp


class AppEngineWarmUpTest(TestCase):
  """Test the APP Engine public endpoint."""

  def test_warmup_returns_correct_html(self):
    request = HttpRequest()
    request.method = 'GET'
    response = WarmUp.as_view()(request)

    assert response.status_code == 200
    assert response.content.decode('utf8') == 'OK'

  def test_warmup_routing(self):
    url = reverse('appengine_warmup')
    found = resolve(url)
    self.assertEqual(found.func.view_class, WarmUp)
