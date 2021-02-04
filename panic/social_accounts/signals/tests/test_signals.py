"""Test the Social Accounts Signal Handlers."""

from unittest import mock

from allauth.account.models import EmailAddress
from allauth.socialaccount.signals import pre_social_login
from django.test import override_settings

from ...tests.fixtures.signals import SignalsTestHarness, get_mock_social_login
from .. import presocial_login


class TestSocialConnect(SignalsTestHarness):

  @mock.patch(presocial_login.__name__ + '.process_social_connect')
  def test_social_signup_signal_received(self, m_handler):
    pre_social_login.send(
        'pre_social_login', user=self.user, sociallogin=None, request=''
    )
    m_handler.assert_called()

  @mock.patch(presocial_login.__name__ + '.PreSocialConnector')
  def test_social_connect_instantiates_connector_class(self, mock_class):
    mock_login = get_mock_social_login()
    presocial_login.process_social_connect(None, mock_login)
    mock_class.assert_called_once_with(mock_login)

  @mock.patch(
      presocial_login.__name__ + '.PreSocialConnector.get_user_for_connection'
  )
  def test_social_connect_no_email_returned(self, mock_func):
    mock_func.return_value = None

    sociallogin = get_mock_social_login()
    presocial_login.process_social_connect(None, sociallogin)

    mock_func.assert_called_once()
    sociallogin.connect.assert_not_called()

  @mock.patch(
      presocial_login.__name__ + '.PreSocialConnector.get_user_for_connection'
  )
  def test_social_connect_valid_email_returned(self, mock_func):
    mock_func.return_value = self.user

    sociallogin = get_mock_social_login()
    presocial_login.process_social_connect(None, sociallogin)

    mock_func.assert_called_once()
    sociallogin.connect.assert_called_once_with(None, self.user)


class TestPreSocialConnectClass(SignalsTestHarness):

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    cls.instance = None
    cls.sociallogin = get_mock_social_login()
    cls.email_address = EmailAddress(user=cls.user, email=cls.mock_email.email)

  def create_test_instance(self):
    self.instance = presocial_login.PreSocialConnector(self.sociallogin)

  def set_email_verified(self, value):
    self.email_address.verified = value
    self.email_address.save()

  def test_no_connect_needed_existing(self):
    self.sociallogin.is_existing = True
    self.sociallogin.email_addresses = []

    self.create_test_instance()

    self.assertIsNone(self.instance.get_user_for_connection())

  def test_no_connect_needed_no_emails(self):
    self.sociallogin.is_existing = False
    self.sociallogin.email_addresses = []

    self.create_test_instance()

    self.assertIsNone(self.instance.get_user_for_connection())

  @override_settings(SOCIALACCOUNT_EMAIL_VERIFICATION=False)
  def test_verification_not_req(self):
    self.sociallogin.is_existing = False
    self.sociallogin.email_addresses = [self.mock_email]
    self.set_email_verified(False)

    self.create_test_instance()

    self.assertEqual(self.user, self.instance.get_user_for_connection())

  @override_settings(SOCIALACCOUNT_EMAIL_VERIFICATION=False)
  def test_verification_not_req_no_matching_user(self):
    self.sociallogin.is_existing = False
    self.sociallogin.email_addresses = [self.wrong_email]
    self.set_email_verified(False)

    self.create_test_instance()

    self.assertIsNone(self.instance.get_user_for_connection())

  @override_settings(SOCIALACCOUNT_EMAIL_VERIFICATION=True)
  def test_verification_req_user_unverified(self):
    self.sociallogin.is_existing = False
    self.sociallogin.email_addresses = [self.mock_email]
    self.set_email_verified(False)

    self.create_test_instance()

    self.assertIsNone(self.instance.get_user_for_connection())

  @override_settings(SOCIALACCOUNT_EMAIL_VERIFICATION=True)
  def test_verification_req_user_verified(self):
    self.sociallogin.is_existing = False
    self.sociallogin.email_addresses = [self.mock_email]
    self.set_email_verified(True)

    self.create_test_instance()

    self.assertEqual(self.user, self.instance.get_user_for_connection())

  @override_settings(SOCIALACCOUNT_EMAIL_VERIFICATION=True)
  def test_verification_req_no_matching_user(self):
    self.sociallogin.is_existing = False
    self.sociallogin.email_addresses = [self.wrong_email]
    self.set_email_verified(True)

    self.create_test_instance()

    self.assertIsNone(self.instance.get_user_for_connection())
