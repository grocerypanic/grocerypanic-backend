"""Test Admin command confirmation dialogue."""

from io import StringIO
from unittest.mock import patch

from django.test import TestCase

from .. import confirmation as confirmation_module
from ..confirmation import AdminConfirmation


class TestConfirmation(AdminConfirmation):
  """Test class based from AdminConfirmation."""

  confirm_message = "Are you sure [Y/n] ?"
  confirm_yes = "Y"


class TestAdminConfirmation(TestCase):
  """Test the AdminConfirmation class."""

  def setUp(self):
    self.confirm = TestConfirmation()

  @patch(confirmation_module.__name__ + ".sys.stdout", new_callable=StringIO)
  @patch(confirmation_module.__name__ + '.input', return_value='anything')
  def test_confirm_invalid(self, _, m_stdout):
    response = self.confirm.are_you_sure()
    self.assertFalse(response)
    self.assertIn(TestConfirmation.confirm_message, m_stdout.getvalue())

  @patch(confirmation_module.__name__ + ".sys.stdout", new_callable=StringIO)
  @patch(confirmation_module.__name__ + '.input', return_value='n')
  def test_confirm_valid_negative(self, _, m_stdout):
    response = self.confirm.are_you_sure()
    self.assertFalse(response)
    self.assertIn(TestConfirmation.confirm_message, m_stdout.getvalue())

  @patch(confirmation_module.__name__ + ".sys.stdout", new_callable=StringIO)
  @patch(
      confirmation_module.__name__ + '.input',
      return_value=TestConfirmation.confirm_yes,
  )
  def test_confirm_valid_affirmative(self, _, m_stdout):
    response = self.confirm.are_you_sure()
    self.assertTrue(response)
    self.assertIn(TestConfirmation.confirm_message, m_stdout.getvalue())
