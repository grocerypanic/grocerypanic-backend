"""Test the CSRF endpoint."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from ..csrf_error import csrf_error_view


class PublicCSRFErrorTest(TestCase):
  """Test the public CSRF Error API."""

  def setUp(self):
    self.factory = APIRequestFactory(enforce_csrf_checks=True)
    self.get = self.factory.get('/someView')
    self.post = self.factory.post('/someView')
    self.csrf_error = csrf_error_view

  def test_login_required(self):
    resp = self.csrf_error(self.get)

    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertNotIn(settings.CSRF_COOKIE_NAME, resp.cookies)

  def test_create_login_required(self):
    resp = self.csrf_error(self.post)

    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertNotIn(settings.CSRF_COOKIE_NAME, resp.cookies)


class PrivateCSRFErrorTest(TestCase):
  """Test the private CSRF Error API."""

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )
    self.factory = APIRequestFactory(enforce_csrf_checks=True)
    self.get = self.factory.get('/someView')
    self.post = self.factory.post('/someView')
    self.csrf_error = csrf_error_view
    force_authenticate(self.get, user=self.user)
    force_authenticate(self.post, user=self.user)

  def test_trigger_message_on_post(self):
    resp = self.csrf_error(self.post)
    self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
    self.assertNotIn(settings.CSRF_COOKIE_NAME, resp.cookies)
    self.assertEqual(resp.data, {'error': 'Refresh csrf and try again.'})

  def test_trigger_message_on_get(self):
    resp = self.csrf_error(self.get)
    self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
    self.assertNotIn(settings.CSRF_COOKIE_NAME, resp.cookies)
    self.assertEqual(resp.data, {'error': 'Refresh csrf and try again.'})

  def tearDown(self):
    self.user.delete()
