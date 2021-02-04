"""Test the autoadmin management command."""

from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

User = get_user_model()


class AutoAdminTestCase(TestCase):

  def setUp(self):
    self.output_stdout = StringIO()
    self.output_stderr = StringIO()

  def test_autoadmin_create(self):
    query = User.objects.all().filter(username="admin")
    assert len(query) == 0

    call_command(
        'autoadmin',
        stdout=self.output_stdout,
        stderr=self.output_stderr,
        no_color=True
    )

    assert "Successfully created admin user." in self.output_stdout.getvalue()
    assert self.output_stderr.getvalue() == ""

    query = User.objects.get(username="admin")
    assert query.username == "admin"
    assert query.email == "test@example.com"

  def test_autoadmin_create_twice(self):
    call_command(
        'autoadmin', stdout=StringIO(), stderr=StringIO(), no_color=True
    )

    call_command(
        'autoadmin',
        stdout=self.output_stdout,
        stderr=self.output_stderr,
        no_color=True
    )
    assert "The admin user already exists." in self.output_stdout.getvalue()
    assert self.output_stderr.getvalue() == ""

    query = User.objects.get(username="admin")
    assert query.username == "admin"

    query = User.objects.all().filter(username="admin")
    assert len(query) == 1

  def tearDown(self):
    query = User.objects.all().filter(username="admin")
    if query is not None:
      for row in query:
        row.delete()
