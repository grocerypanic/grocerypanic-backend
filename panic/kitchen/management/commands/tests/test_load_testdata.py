"""Test load_testdata management command."""

from io import StringIO
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from .... import management
from ..load_testdata import ERROR_MESSAGE, SUCCESS_MESSAGE

MANAGEMENT_MODULE = management.__name__


class CommandTestInvalid(TestCase):
  """Test the load_testdata command with an invalid user."""

  def test_invalid_user_specified_stdout(self):
    output_stdout = StringIO()
    output_stderr = StringIO()
    call_command(
        'load_testdata',
        "non-existent-user",
        stdout=output_stdout,
        stderr=output_stderr,
        no_color=True
    )

    self.assertIn(
        ERROR_MESSAGE,
        output_stderr.getvalue(),
    )
    self.assertEqual(output_stdout.getvalue(), "")


class CommandTestValid(TestCase):
  """Test the load_testdata command with a valid user."""

  @classmethod
  def setUpTestData(cls):
    cls.output_stdout = StringIO()
    cls.output_stderr = StringIO()
    cls.user = get_user_model().objects.create_user(
        username="created_test_user",
        email="created_test_user@niallbyrne.ca",
        password="test123",
    )

  def setUp(self):

    with patch(
        f"{MANAGEMENT_MODULE}.commands.load_testdata.BulkTestDataGenerator"
    ) as generator:

      self.mock_generator = Mock()
      self.mock_generator.generate_data = Mock()
      generator.return_value = self.mock_generator
      self.generator = generator

      call_command(
          'load_testdata',
          self.user.username,
          stdout=self.output_stdout,
          stderr=self.output_stderr,
          no_color=True
      )

  def test_instantiates_the_generator_class(self):
    self.generator.assert_called_once_with(self.user.username)
    self.mock_generator.generate_data.assert_called_once()
    self.assertIn(
        SUCCESS_MESSAGE,
        self.output_stdout.getvalue(),
    )
