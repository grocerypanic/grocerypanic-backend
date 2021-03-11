"""Test the create_social_app function."""

import os
from unittest import mock

from allauth.socialaccount.models import SocialApp
from django.contrib.auth import get_user_model
from django.test import TestCase
from parameterized import parameterized_class

from ..social_app import (
    ALREADY_EXISTS_ERROR,
    ENVIRONMENT_VARIABLE_ERROR,
    create_social_app,
)

User = get_user_model()
PROVIDERS = [{"provider": "facebook"}, {"provider": "google"}]
MOCK_SECRET_VALUE = "mock_secret"
MOCK_ID_VALUE = "mock_id"


def environment_mock():
  mock_env = dict()
  for provider in PROVIDERS:
    provider_name = provider['provider'].upper()
    mock_env[f'{provider_name}_ID'] = MOCK_ID_VALUE
    mock_env[f'{provider_name}_SECRET_KEY'] = MOCK_SECRET_VALUE
  return mock_env


@parameterized_class(PROVIDERS)
class TestCreateSocialApp(TestCase):
  """Test the create_social_app function."""

  def tearDown(self):
    SocialApp.objects.all().delete()

  @mock.patch.dict(os.environ, {})
  def test_create_no_env_vars(self):
    exists = SocialApp.objects.all().filter(provider=self.provider).count()
    assert exists == 0

    with self.assertRaises(Exception) as raised:
      create_social_app(self.provider)

    self.assertEqual(raised.exception.args[0], ENVIRONMENT_VARIABLE_ERROR)

  @mock.patch.dict(os.environ, environment_mock())
  def test_create(self):
    exists = SocialApp.objects.all().filter(provider=self.provider).count()
    assert exists == 0

    create_social_app(self.provider)

    app = SocialApp.objects.get(provider=self.provider)
    assert app.client_id == MOCK_ID_VALUE
    assert app.secret == MOCK_SECRET_VALUE

  @mock.patch.dict(os.environ, environment_mock())
  def test_create_twice(self):
    create_social_app(self.provider)
    with self.assertRaises(Exception) as raised:
      create_social_app(self.provider)

    self.assertEqual(raised.exception.args[0], ALREADY_EXISTS_ERROR)
