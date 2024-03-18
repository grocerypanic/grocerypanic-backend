"""Test the PatchedAccessToken class."""

from django.contrib.auth import get_user_model
from django.db.models import Model
from django.test import TestCase
from rest_framework_simplejwt.tokens import Token, TokenError

from ..patched_access_token import PatchedAccessToken

User: Model = get_user_model()


class PatchedAccessTokenTest(TestCase):
  """Test the PatchedAccessToken class."""

  def setUp(self):
    self.user = User.objects.create_user(
        username="testuser1",
        email="test1@niallbyrne.ca",
        password="test123",
    )

  def test_for_user__active_user__valid_token(self):
    self.user.is_active = True

    token = PatchedAccessToken.for_user(self.user)
    self.assertIsInstance(token, Token)

  def test_for_user__active_user__raises_exception(self):
    self.user.is_active = False

    with self.assertRaises(TokenError) as exc:
      PatchedAccessToken.for_user(self.user)

    self.assertEqual(str(exc.exception), "Token is invalid or expired")
