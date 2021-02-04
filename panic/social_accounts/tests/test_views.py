"""Ensure All Social Views Are Present"""

from django.test import TestCase
from django.urls import reverse


class TestSocialViewsArePresent(TestCase):

  def test_google_login(self):
    reverse("social_accounts:google_login")

  def test_fb_login(self):
    reverse("social_accounts:fb_login")
