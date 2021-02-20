"""Test the V1 spa_security CSRF API endpoint."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from .bases import (
    APICrudTestHarnessUnauthorized,
    AuthenticationRegistrationTestHarness,
)

USER_AUTH_CSRF = reverse('spa_security:csrf')

User = get_user_model()


class CSRFAuthorization(AuthenticationRegistrationTestHarness):
  """Test the CSRF authentication API endpoints with user data."""

  def test_auth_csrf(self):
    self._data_generate_user(has_profile_initialized=True, verified=True)
    self._login()

    url = self._build_url(USER_AUTH_CSRF)

    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertIsNotNone(response.json()['token'])


class CSRFUnauthorized(APICrudTestHarnessUnauthorized):
  """Test the CSRF authorization API endpoint anonymously."""

  test_view = 'spa_security:csrf'
  __test__ = True
  __pk_checks__ = False
