"""Test the app engine app views."""

from unittest.mock import patch

from django.http import HttpRequest
from django.test import TestCase
from django.urls import resolve, reverse
from rest_framework import status

from .. import views as views_module
from ..views import DATABASE_WAIT_INTERVAL, WarmUp


class AppEngineWarmUpTest(TestCase):
  """Test the APP Engine public endpoint."""

  def setUp(self):
    self.request = HttpRequest()
    self.request.method = 'GET'

  def test_warmup_returns_correct_html(self):
    response = WarmUp.as_view()(self.request)

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )
    self.assertEqual(
        response.content.decode('utf8'),
        'OK',
    )

  def test_warmup_routing(self):
    url = reverse('appengine_warmup')
    found = resolve(url)
    self.assertEqual(found.func.view_class, WarmUp)

  @patch(views_module.__name__ + ".wait_for_database_connection")
  def test_warm_up_waits_for_database(self, m_wait):
    WarmUp.as_view()(self.request)
    m_wait.assert_called_once_with(DATABASE_WAIT_INTERVAL)

  @patch(views_module.__name__ + ".import_module")
  def test_warm_up_imports_modules(self, m_import):
    WarmUp.as_view()(self.request)
    m_import.assert_called()
