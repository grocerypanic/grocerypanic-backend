"""Test the CSRF endpoint."""

from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CSRF_URL = reverse("spa_security:csrf")


class PublicCSRFTest(TestCase):
  """Test the public CSRF API."""

  def setUp(self):
    self.client = APIClient()

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

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )
    self.client = APIClient(enforce_csrf_checks=True)
    self.client.force_authenticate(self.user)

  @patch(
      "django.middleware.csrf._salt_cipher_secret",
      new_callable=Mock(return_value=lambda x: "MockToken")
  )
  def test_retrieve_message(self, _):
    resp = self.client.get(CSRF_URL)

    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    self.assertEqual(resp.data["token"], "MockToken")
    self.assertIn(settings.CSRF_COOKIE_NAME, resp.cookies)

  def tearDown(self):
    self.user.delete()
