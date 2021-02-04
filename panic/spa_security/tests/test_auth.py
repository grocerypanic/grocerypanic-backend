"""Test the Cookie Authentication"""

from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework_simplejwt.exceptions import InvalidToken

from ..auth import JWTCookieAuthentication


class CookieAuthenticatorTest(TestCase):
  """Test the Cookie Authenticator"""

  def setUp(self):
    self.factory = RequestFactory()
    self.request = self.factory.get('/fakeEndpoint')
    self.auth = JWTCookieAuthentication()
    self.cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)

  @patch(
      'rest_framework_simplejwt.authentication.JWTAuthentication.'
      'get_validated_token'
  )
  def test_authentication_fails_by_default(self, validate):
    """Test that login is required for retrieving shelves."""

    self.request.COOKIES = {}
    self.request.headers = {}
    self.assertIsNone(self.auth.authenticate(self.request))
    assert not validate.called

  @patch(
      'rest_framework_simplejwt.authentication.JWTAuthentication.'
      'get_user'
  )
  def test_authentication_validates_cookie_invalid(self, validate):

    validate.return_value = "Validated"

    self.request.COOKIES[self.cookie_name] = "Random String"
    with self.assertRaises(InvalidToken):
      self.auth.authenticate(self.request)
      assert validate.called

  @patch(
      'rest_framework_simplejwt.authentication.JWTAuthentication.'
      'get_validated_token'
  )
  @patch(
      'rest_framework_simplejwt.authentication.JWTAuthentication.'
      'get_user'
  )
  def test_authentication_validates_cookie_valid(self, user, validate):

    user.return_value = "User"
    validate.return_value = "Validated"

    self.request.COOKIES[self.cookie_name] = "Random String"
    self.assertEqual((user.return_value, validate.return_value),
                     self.auth.authenticate(self.request))
    assert validate.called
    assert user.called

  @patch(
      'rest_framework_simplejwt.authentication.JWTAuthentication.'
      'get_validated_token'
  )
  def test_authentication_another_cookie(self, validate):

    self.request.COOKIES["ANOTHER_COOKIE"] = "Random String"
    self.assertIsNone(self.auth.authenticate(self.request))
    assert not validate.called

  @patch(
      'rest_framework_simplejwt.authentication.JWTAuthentication.'
      'get_validated_token'
  )
  def test_authentication_no_auth_cookie(self, validate):

    with self.settings(JWT_AUTH_COOKIE=None):
      self.assertIsNone(self.auth.authenticate(self.request))
      assert not validate.called
