"""Fixtures for the allauth library."""

from unittest.mock import Mock


class MockSocialLogin:
  """Test double for an allauth SocialLogin model."""

  def __init__(self):
    self.connect = Mock()
    self.email_addresses = []
    self.is_existing = False


class MockEmail:
  """Test double for an allauth email model object."""

  def __init__(self, email):
    self.email = email
