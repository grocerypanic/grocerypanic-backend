"""Test the tos view."""

from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status

TOS_URL = reverse("legal_tos")


class LegalTosTest(SimpleTestCase):
  """Test the legal TOS view."""

  def test_returns_correct_html(self,):
    response = self.client.get(TOS_URL)

    self.assertEqual(
        response.status_code,
        status.HTTP_200_OK,
    )
    self.assertTemplateUsed(response, 'tos.html')
