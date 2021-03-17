"""Test the privacy policy view."""

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status

TOS_URL = reverse("legal_privacypolicy")


class LegalPrivacyTest(SimpleTestCase):
  """Test the legal PrivacyPolicy view."""

  def test_returns_correct_html(self,):
    response = self.client.get(TOS_URL)

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )
    self.assertTemplateUsed(response, 'privacy.html')
