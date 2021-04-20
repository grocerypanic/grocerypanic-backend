"""Test the views for the user app."""

import pytz
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .. import views as view_module

TIMEZONE_URL = reverse("user:timezones")
VIEW_MODULE = view_module.__name__


class PublicTimezoneTest(TestCase):
  """Test the public Timezone API."""

  def test_login_required(self):
    resp = self.client.get(TIMEZONE_URL)
    self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTimezoneTest(TestCase):
  """Test the private CSRF API."""

  @classmethod
  def setUpTestData(cls):
    cls.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )

  def setUp(self):
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def test_timezone_list(self):
    resp = self.client.get(TIMEZONE_URL)

    timezones = list(pytz.common_timezones)
    timezones.sort()

    expected = []

    for index, timezone in enumerate(timezones):
      expected.append({"id": index, "name": timezone})

    self.assertEqual(resp.status_code, status.HTTP_200_OK)
    self.assertEqual(resp.data, expected)
