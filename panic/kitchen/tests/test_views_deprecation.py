"""Test API Deprecation Utils"""

from datetime import date
from unittest import TestCase

from rest_framework import status
from rest_framework.response import Response

from ..views.deprecation import (
    DEPRECATED_WARNING,
    deprecated_response,
    deprecated_warning,
)


class TestDeprecationWarning(TestCase):
  """Test the deprecated_warning function"""

  def setUp(self):
    self.mock_response = Response(
        {"data": "mock_data"},
        status=status.HTTP_200_OK,
    )

  def test_headers_are_set_with_sunset(self):
    sunset = date(year=2021, month=3, day=1)
    res = deprecated_warning(self.mock_response, sunset)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res['Deprecation'], str(sunset))
    self.assertEqual(res['Warning'], DEPRECATED_WARNING)
    self.assertEqual(res['Sunset'], str(sunset))


class TestDeprecatedResponse(TestCase):
  """Test the deprecated_response function"""

  def test_response(self):
    message = "Test Message"
    res = deprecated_response(message)
    self.assertEqual(res.status_code, status.HTTP_410_GONE)
    self.assertEqual(res.data, {"detail": message})
