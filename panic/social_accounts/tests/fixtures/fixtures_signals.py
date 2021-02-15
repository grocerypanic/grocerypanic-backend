"""Signals test fixtures."""

from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase

User = get_user_model()


def get_mock_social_login():
  """Generate a django-allauth sociallogin test double."""

  mock_social_login = Mock()
  mock_social_login.connect = Mock()
  mock_social_login.email_addresses = []

  return mock_social_login


class MockEmail:
  """Test double for a django-allauth email model object."""

  def __init__(self, email):
    self.email = email


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
