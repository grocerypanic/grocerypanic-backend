"""Test the app engine app views."""

from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from .. import views as views_module

WARMUP_URL = reverse("appengine_warmup")
VIEWS_MODULE = views_module.__name__


@patch(f"{VIEWS_MODULE}.wait_for_database_connection")
@patch(f"{VIEWS_MODULE}.warm_module_cache")
class AppEngineWarmUpTest(TestCase):
  """Test the APP Engine public endpoint."""

  def test_warmup_returns_correct_html(self, _unused1, _unused2):
    response = self.client.get(WARMUP_URL)

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )
    self.assertEqual(
        response.content.decode('utf8'),
        'OK',
    )

  def test_warm_up_waits_for_database(self, _, m_wait):
    self.client.get(WARMUP_URL)
    m_wait.assert_called_once_with(settings.WARM_UP_DATABASE_WAIT_INTERVAL)

  def test_warm_up_imports_modules(self, m_warm, _):
    self.client.get(WARMUP_URL)
    m_warm.assert_called()
