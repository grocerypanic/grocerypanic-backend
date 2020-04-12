"""Test the CSRF endpoint."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from ..views import csrf_error


class PublicCSRFErrorTest(TestCase):
  """Test the public CSRF Error API"""

  def setUp(self) -> None:
    self.factory = APIRequestFactory(enforce_csrf_checks=True)
    self.get = self.factory.get('/someView')
    self.post = self.factory.post('/someView')
    self.csrf_error = csrf_error

  def test_login_required(self):
    """Test that login is required for retrieving csrf."""
    resp = self.csrf_error(self.get)

    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertNotIn('csrftoken', resp.cookies)

  def test_create_login_required(self):
    resp = self.csrf_error(self.post)

    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
    self.assertNotIn('csrftoken', resp.cookies)


class PrivateCSRFErrorTest(TestCase):
  """Test the private CSRF Error API"""

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )
    self.factory = APIRequestFactory(enforce_csrf_checks=True)
    self.get = self.factory.get('/someView')
    self.post = self.factory.post('/someView')
    self.csrf_error = csrf_error
    force_authenticate(self.get, user=self.user)
    force_authenticate(self.post, user=self.user)

  def test_trigger_message_on_post(self):
    resp = self.csrf_error(self.post)
    self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
    self.assertNotIn('csrftoken', resp.cookies)
    self.assertEqual(resp.data, {'error': 'Refresh csrf and try again.'})

  def test_trigger_message_on_get(self):
    resp = self.csrf_error(self.get)
    self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
    self.assertNotIn('csrftoken', resp.cookies)
    self.assertEqual(resp.data, {'error': 'Refresh csrf and try again.'})

  def tearDown(self):
    self.user.delete()
