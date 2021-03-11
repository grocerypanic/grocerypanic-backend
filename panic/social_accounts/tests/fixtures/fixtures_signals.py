"""Signals test fixtures."""

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase

from .fixtures_allauth import MockEmail

User = get_user_model()


class SignalsTestHarness(TestCase):
  """Test harness for testing django-all-auth social signals."""

  user: Model
  mock_email: MockEmail

  @classmethod
  def setUpTestData(cls):
    cls.test_user = "testuser1"
    cls.mock_email = MockEmail("testuser@test.com")
    cls.wrong_email = MockEmail("wrong_email_address_for_user")

    cls.user = User(username=cls.test_user, email=cls.mock_email.email)
    cls.user.set_password('my password string')
    cls.user.save()
