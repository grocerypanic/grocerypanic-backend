"""Fixtures for User app signal handlers."""

from allauth.account.signals import user_signed_up
from django.contrib.auth import get_user_model
from django.test import TestCase

from ...tests.fixtures.fixtures_django import MockRequest


class SignalTestHarness(TestCase):
  """Test harness for django allauth signals."""

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
