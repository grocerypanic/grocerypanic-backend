"""Ensure all social account views are present."""

from django.test import TestCase
from django.urls import reverse


class TestSocialViewsArePresent(TestCase):
  """Test resolution of social login views."""

  def test_google_login(self):
    reverse("social_accounts:google_login")

  def test_fb_login(self):
    reverse("social_accounts:fb_login")
