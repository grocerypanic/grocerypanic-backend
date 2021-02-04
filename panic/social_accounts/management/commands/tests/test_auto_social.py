"""Test the autosocial.facebook management command."""

from io import StringIO
from unittest import mock

from allauth.socialaccount.models import SocialApp
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from parameterized import parameterized_class

User = get_user_model()

PROVIDERS = [{"provider": "facebook"}, {"provider": "google"}]


@parameterized_class(PROVIDERS)
class AutoSocialTestCase1(TestCase):

  def __clear_social_accounts(self):
    query = SocialApp.objects.all()
    if query is not None:
      for row in query:
        row.delete()

  def setUp(self):
    self.__clear_social_accounts()

  def tearDown(self):
    self.__clear_social_accounts()

  @mock.patch('os.getenv')
  def test_autoadmin_create_no_env_vars(self, environ):
    environ.return_value = None
    query = SocialApp.objects.all().filter(provider=self.provider)
    assert len(query) == 0

    output_stdout = StringIO()
    output_stderr = StringIO()
    call_command(
        'autosocial',
        self.provider,
        stdout=output_stdout,
        stderr=output_stderr,
        no_color=True
    )
    assert 'The required env vars are not set.' in output_stderr.getvalue()
    assert output_stdout.getvalue() == ""

    query = SocialApp.objects.all().filter(provider=self.provider)
    assert len(query) == 0

  @mock.patch('os.getenv')
  def test_autoadmin_create(self, environ):
    environ.return_value = "not_very_random_string"

    query = SocialApp.objects.all().filter(provider=self.provider)
    assert len(query) == 0

    output_stdout = StringIO()
    output_stderr = StringIO()
    call_command(
        'autosocial',
        self.provider,
        stdout=output_stdout,
        stderr=output_stderr,
        no_color=True
    )
    assert 'Successfully created social app account.' in output_stdout.getvalue(
    )
    assert output_stderr.getvalue() == ""

    query = SocialApp.objects.get(provider=self.provider)
    assert query.client_id == "not_very_random_string"
    assert query.secret == "not_very_random_string"

  @mock.patch('os.getenv')
  def test_autoadmin_create_twice(self, environ):
    environ.return_value = "not_very_random_string"

    output_stdout = StringIO()
    output_stderr = StringIO()
    call_command(
        'autosocial',
        self.provider,
        stdout=output_stdout,
        stderr=output_stderr,
        no_color=True
    )

    output_stdout = StringIO()
    output_stderr = StringIO()
    call_command(
        'autosocial',
        self.provider,
        stdout=output_stdout,
        stderr=output_stderr,
        no_color=True
    )
    assert 'The social app already exists.' in output_stderr.getvalue()
    assert output_stdout.getvalue() == ""

    query = SocialApp.objects.get(provider=self.provider)
    assert query.client_id == "not_very_random_string"
    assert query.secret == "not_very_random_string"

    query = SocialApp.objects.all().filter(provider=self.provider)
    assert len(query) == 1
