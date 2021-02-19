"""Test Django All Auth Signup Signal Receiver for the User Model"""

from unittest.mock import patch

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.test import TestCase

from ...tests.fixtures.django import MockRequest
from .. import signup


class SignalTestHarness(TestCase):

  def trigger(self, request):
    user_signed_up.send(sender=request, request=request, user=self.user)

  def setUp(self):
    self.user = get_user_model().objects.create(
        username="test1",
        email="test@example.com",
        password="12345678",
    )
    self.request = MockRequest()

  def tearDown(self):
    self.user.delete()


class TestSignalHandler(SignalTestHarness):

  @patch(signup.__name__ + ".user_signed_up_event")
  def test_signal_received(self, m_event):
    request = MockRequest()
    self.trigger(request)
    m_event.assert_called_with(request, self.user)