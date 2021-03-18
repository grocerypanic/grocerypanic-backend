"""Test the CSRF endpoint."""

from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .. import csrf_token as view_module

CSRF_URL = reverse("spa_security:csrf")
VIEW_MODULE = view_module.__name__


class PublicCSRFTest(TestCase):
  """Test the public CSRF API."""

  def test_login_required(self):
    resp = self.client.get(CSRF_URL)

    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertNotIn(settings.CSRF_COOKIE_NAME, resp.cookies)

  def test_create_login_required(self):
    payload = {}
    resp = self.client.post(CSRF_URL, payload)

    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertNotIn(settings.CSRF_COOKIE_NAME, resp.cookies)


class PrivateCSRFTest(TestCase):
  """Test the private CSRF API."""

  @classmethod
  def setUpTestData(cls):
    cls.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )

  def setUp(self):
    self.client = APIClient(enforce_csrf_checks=True)
    self.client.force_authenticate(self.user)

  @patch(
      VIEW_MODULE + '.get_token',
      new_callable=Mock(return_value=lambda x: "MockToken")
  )
  def test_token_is_set(self, _):
    resp = self.client.get(CSRF_URL)

    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    self.assertEqual(resp.data["token"], "MockToken")

  def test_cookie_is_set(self):
    resp = self.client.get(CSRF_URL)

    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    self.assertIn(settings.CSRF_COOKIE_NAME, resp.cookies)
