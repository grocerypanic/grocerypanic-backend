"""Test the V1 token authorization API endpoints."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from .bases import AuthenticationRegistrationTestHarness

USER_AUTH_CSRF = reverse('spa_security:csrf')
USER_TOKEN_REFRESH = reverse('token_refresh')
USER_TOKEN_VERIFY = reverse('token_verify')

User = get_user_model()


class TokenAuthorization(AuthenticationRegistrationTestHarness):
  """Test the token authorization API endpoints with user data."""

  def test_auth_csrf(self):
    self._data_generate_user(has_profile_initialized=True, verified=True)
    self._login()

    url = self._build_url(USER_AUTH_CSRF)

    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIsNotNone(response.json()['token'])

  def test_auth_user_token_refresh(self):
    self._data_generate_user(has_profile_initialized=True, verified=True)
    tokens = self._login().json()

    token_data = {
        'refresh': tokens['refresh_token'],
    }

    url = self._build_url(USER_TOKEN_REFRESH)

    response = self.client.post(url, token_data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIsNotNone(response.json()['access'])

  def test_auth_user_token_verify(self):
    self._data_generate_user(has_profile_initialized=True, verified=True)
    self._login()

    jwt_token = self.client.cookies.get(settings.JWT_AUTH_COOKIE)

    token_data = {
        'token': jwt_token,
    }

    self._logout()

    url = self._build_url(USER_TOKEN_VERIFY)

    response = self.client.post(url, token_data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), {})


class TokenUnauthorizedInvalid(AuthenticationRegistrationTestHarness):
  """Test the V1 Authentication/Registration API endpoints without user data."""

  def test_auth_user_token_refresh_no_auth(self):
    token_data = {'refresh': "Invalid Data"}

    url = self._build_url(USER_TOKEN_REFRESH)

    response = self.client.post(url, token_data)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_auth_user_token_verify_no_auth(self):
    token_data = {'token': "Invalid Data"}

    url = self._build_url(USER_TOKEN_VERIFY)

    response = self.client.post(url, token_data)
    self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
