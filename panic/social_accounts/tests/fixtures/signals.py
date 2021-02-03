"""Signals Test Harness"""

from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase

User = get_user_model()


def get_mock_social_login():

  mock_social_login = Mock()
  mock_social_login.connect = Mock()
  mock_social_login.email_addresses = []

  return mock_social_login


class MockEmail:

  def __init__(self, email):
    self.email = email


class SignalsTestHarness(TestCase):
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
