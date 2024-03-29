"""Test the custom csrf mixins."""

from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from ..csrf import CSRFMixin


class PlaceboTest(APIView):
  """Mocked API view without the CSRFMixin."""

  def get(self, request):  # pylint: disable=unused-argument
    return Response({}, status=HTTP_200_OK)

  def post(self, request):  # pylint: disable=unused-argument
    return Response({}, status=HTTP_200_OK)


class Ensured(CSRFMixin, APIView):
  """Mocked API view with the CSRFMixin."""

  def get(self, request):  # pylint: disable=unused-argument
    return Response({}, status=HTTP_200_OK)

  def post(self, request):  # pylint: disable=unused-argument
    return Response({}, status=HTTP_200_OK)


class TestCSRFMixin(TestCase):
  """Test the CSRFMixin."""

  def setUp(self):
    self.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )
    self.factory = APIRequestFactory(enforce_csrf_checks=True)
    self.get = self.factory.get('/someView')
    self.post = self.factory.post('/someView')
    self.placebo = PlaceboTest.as_view()
    self.ensured = Ensured.as_view()
    force_authenticate(self.get, user=self.user)
    force_authenticate(self.post, user=self.user)

  @patch('django.middleware.csrf.CsrfViewMiddleware._get_token')
  def test_placebo_get(self, get_token):
    self.placebo(self.get)
    self.assertFalse(get_token.called)

  @patch('django.middleware.csrf.CsrfViewMiddleware._get_token')
  def test_placebo_post(self, get_token):
    self.placebo(self.post)
    self.assertFalse(get_token.called)

  @patch('django.middleware.csrf.CsrfViewMiddleware._get_token')
  def test_ensured_get(self, get_token):
    self.ensured(self.get)
    self.assertTrue(get_token.called)

  @patch('django.middleware.csrf.CsrfViewMiddleware._get_token')
  def test_ensured_post(self, get_token):
    self.ensured(self.post)
    self.assertTrue(get_token.called)

  def tearDown(self):
    self.user.delete()
