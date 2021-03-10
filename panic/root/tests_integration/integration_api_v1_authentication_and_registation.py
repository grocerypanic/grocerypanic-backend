"""Test the V1 user management API endpoints."""

import re

from allauth.account.models import EmailConfirmationHMAC
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status

from .bases import (
    APICrudTestHarnessUnauthorized,
    AuthenticationRegistrationTestHarness,
)

USER_CONFIRMATION_EMAIL_SEND = reverse('account_email_verification_sent')
USER_DETAILS = reverse('rest_user_details')
USER_LOGIN = reverse('rest_login')
USER_LOGOUT = reverse('rest_logout')
USER_PASSWORD_CHANGE = reverse('rest_password_change')
USER_PASSWORD_RESET = reverse('rest_password_reset')
USER_PASSWORD_RESET_CONFIRM = reverse('rest_password_reset_confirm')
USER_REGISTRATION = reverse('rest_register')

User = get_user_model()


class UserDetails(AuthenticationRegistrationTestHarness):
  """Test the user details API endpoint."""

  def _create_expected_details_response(self, user):
    user.refresh_from_db()
    expected_response = dict(self.user_base_data)
    expected_response.update({
        "id": user.id,
        "first_name": "",
        "last_name": "",
        "language_code": self.language_code,
        "has_profile_initialized": user.has_profile_initialized,
        "timezone": self.timezone,
    })
    return expected_response

  def test_user_details_profile_uninitialized(self):
    user, _ = self._data_generate_user(
        has_profile_initialized=False,
        verified=True,
    )
    self._login()

    expected_response = self._create_expected_details_response(user)

    url = self._build_url(USER_DETAILS)
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), expected_response)

  def test_user_details_has_profile_initialized(self):
    user, _ = self._data_generate_user(
        has_profile_initialized=True,
        verified=True,
    )
    self._login()

    expected_response = self._create_expected_details_response(user)

    url = self._build_url(USER_DETAILS)
    response = self.client.get(url)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), expected_response)

  def test_user_details_profile_patch(self):
    user, _ = self._data_generate_user(
        has_profile_initialized=False,
        verified=True,
    )
    self._login()

    expected_response = self._create_expected_details_response(user)
    expected_response.update({'has_profile_initialized': True})

    url = self._build_url(USER_DETAILS)
    response = self.client.patch(url, {'has_profile_initialized': True})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), expected_response)

  def test_user_details_profile_put(self):
    user, _ = self._data_generate_user(
        has_profile_initialized=False,
        verified=True,
    )
    self._login()

    expected_response = self._create_expected_details_response(user)
    expected_response.update({'has_profile_initialized': True})

    url = self._build_url(USER_DETAILS)
    response = self.client.patch(url, expected_response)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), expected_response)


class UserDetailsUnauthorized(AuthenticationRegistrationTestHarness):
  """Test the user details API endpoints anonymously."""

  test_view = 'rest_user_details'
  __test__ = True

  methods_with_pk = {
      'get': status.HTTP_404_NOT_FOUND,
      'put': status.HTTP_404_NOT_FOUND,
      'patch': status.HTTP_404_NOT_FOUND,
      'post': status.HTTP_404_NOT_FOUND,
      'options': status.HTTP_404_NOT_FOUND,
  }


class UserPasswordManagement(AuthenticationRegistrationTestHarness):
  """Test the user password management API endpoints."""

  def test_user_password_reset_request(self):
    user, _ = self._data_generate_user(
        has_profile_initialized=True,
        verified=True,
    )

    url = self._build_url(USER_PASSWORD_RESET)
    expected_response = {'detail': 'Password reset e-mail has been sent.'}

    response = self.client.post(url, {"email": user.email})
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), expected_response)

  def test_user_password_reset_confirm(self):
    user, _ = self._data_generate_user(has_profile_initialized=True)

    token = self.generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    url = self._build_url(USER_PASSWORD_RESET_CONFIRM)

    reset_url = f"{url}{uid}/{token}/"
    reset_data = {
        "new_password1": "changed12345",
        "new_password2": "changed12345",
        "token": token,
        "uid": uid,
    }

    response = self.client.post(reset_url, data=reset_data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(
        response.json(),
        {'detail': 'Password has been reset with the new password.'},
    )

  def test_user_password_change(self):
    self._data_generate_user(
        has_profile_initialized=True,
        verified=True,
    )
    self._login()

    change_data = {
        'old_password': self.password,
        'new_password1': "newpassword1234",
        'new_password2': "newpassword1234",
    }

    url = self._build_url(USER_PASSWORD_CHANGE)
    expected_response = {'detail': 'New password has been saved.'}

    response = self.client.post(url, change_data)
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(response.json(), expected_response)


class UserPasswordChangeUnauthorized(APICrudTestHarnessUnauthorized):
  """Test the user password change API endpoints anonymously."""

  test_view = 'rest_password_change'
  __test__ = True
  __pk_checks__ = False


class UserRegistration(AuthenticationRegistrationTestHarness):
  """Test registration API endpoints, ensure login registration restrictions."""

  def setUp(self):
    mail.outbox.clear()
    super().setUp()

  def _check_message(self, index, expected):
    message = mail.outbox[index]

    self.assertEqual(expected['from_email'], message.from_email)
    self.assertEqual(expected['to'], message.to)
    self.assertEqual(expected['subject'], message.subject)
    if 'body' in expected.keys():
      self.assertEqual(expected['body'], message.body)

  def test_login_email_is_unverified(self):
    self._data_generate_user(verified=False)

    self._login(expected_status=status.HTTP_400_BAD_REQUEST)

  def test_login_email_is_verified(self):
    self._data_generate_user(verified=True)

    self._login()

  def test_user_account_confirmation_process(self):
    _, email = self._data_generate_user(has_profile_initialized=True)

    confirmation = EmailConfirmationHMAC(email)
    confirmation.send(None)
    confirmation_data = {"key": confirmation.key}

    email_confirmation_url = self._build_url(USER_CONFIRMATION_EMAIL_SEND)

    response = self.client.post(
        email_confirmation_url,
        data=confirmation_data,
    )

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.assertDictEqual(
        response.json(),
        {'detail': 'ok'},
    )

    self.assertFalse(email.verified)

    response = self.client.get(f"{email_confirmation_url}{confirmation.key}/",)
    email.refresh_from_db()
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    self.assertEqual(response.url, f"{self._build_url(USER_LOGIN)}")
    self.assertTrue(email.verified)

  def test_user_registration_process(self):
    url = self._build_url(USER_REGISTRATION)
    response = self.client.post(url, self.user_registration_data)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    user = self._query_for_user()
    email = self._query_for_email(user)

    self.assertFalse(email.verified)
    self.assertEqual(len(mail.outbox), 1)

    current_site = Site.objects.get_current()

    expected_message = {
        'subject':
            f"[{current_site.domain}] Please Confirm Your E-mail Address",
        'from_email':
            f"no-reply@{current_site.domain}",
        'to': [user.email],
    }

    self._check_message(0, expected_message)

    regex_match = re.match(
        r".*(http://testserver\S+).*", mail.outbox[0].body, re.DOTALL
    )

    confirmation_url = regex_match.group(1).replace(
        'http://testserver', self.live_server_url
    )

    response = self.client.get(confirmation_url)
    email.refresh_from_db()
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    self.assertEqual(response.url, f"{self._build_url(USER_LOGIN)}")
    self.assertTrue(email.verified)
