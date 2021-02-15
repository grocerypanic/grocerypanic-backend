"""Test the custom samesite middleware mixin."""

from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase, override_settings

from ..mixins import SameSiteMiddleware


class TestSameSiteMiddleware(TestCase):
  """Test the SameSiteMiddleware class."""

  def setUp(self):
    self.response = HttpResponse()
    self.mixin = SameSiteMiddleware()

  @override_settings()
  def test_csrf_cookie_defaults(self):
    del settings.CSRF_COOKIE_SECURE
    del settings.CSRF_COOKIE_SAMESITE
    cookie_name = settings.CSRF_COOKIE_NAME
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertEqual(self.response.cookies[cookie_name]['samesite'], 'None')
    self.assertFalse(self.response.cookies[cookie_name]['secure'])

  @override_settings(CSRF_COOKIE_SAMESITE=None)
  def test_csrf_cookie_same_site_none(self):
    cookie_name = settings.CSRF_COOKIE_NAME
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertEqual(self.response.cookies[cookie_name]['samesite'], 'None')

  @override_settings(CSRF_COOKIE_SAMESITE="lax")
  def test_csrf_cookie_same_site_lax(self):
    cookie_name = settings.CSRF_COOKIE_NAME
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertNotEqual(self.response.cookies[cookie_name]['samesite'], 'None')

  @override_settings(CSRF_COOKIE_SECURE=False)
  def test_csrf_cookie_same_site_not_secure(self):
    cookie_name = settings.CSRF_COOKIE_NAME
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertFalse(self.response.cookies[cookie_name]['secure'])

  @override_settings(CSRF_COOKIE_SECURE=True)
  def test_csrf_cookie_same_site_secure(self):
    cookie_name = settings.CSRF_COOKIE_NAME
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertTrue(self.response.cookies[cookie_name]['secure'])

  @override_settings()
  def test_jwt_cookie_defaults(self):
    del settings.JWT_AUTH_COOKIE_SAMESITE
    del settings.REST_COOKIES_SECURE
    cookie_name = settings.JWT_AUTH_COOKIE
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertEqual(self.response.cookies[cookie_name]['samesite'], 'None')
    self.assertFalse(self.response.cookies[cookie_name]['secure'])

  @override_settings(JWT_AUTH_COOKIE_SAMESITE="lax")
  def test_jwt_cookie_same_site_lax(self):
    cookie_name = settings.JWT_AUTH_COOKIE
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertEqual(self.response.cookies[cookie_name]['samesite'], 'lax')

  @override_settings(JWT_AUTH_COOKIE_SAMESITE=None)
  def test_jwt_cookie_same_site_none(self):
    cookie_name = settings.JWT_AUTH_COOKIE
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertEqual(self.response.cookies[cookie_name]['samesite'], 'None')

  @override_settings(REST_COOKIES_SECURE=False)
  def test_jwt_cookie_same_site_not_secure(self):
    cookie_name = settings.JWT_AUTH_COOKIE
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertFalse(self.response.cookies[cookie_name]['secure'])

  @override_settings(REST_COOKIES_SECURE=True)
  def test_jwt_cookie_same_site_secure(self):
    cookie_name = settings.JWT_AUTH_COOKIE
    self.response.set_cookie(cookie_name, "somevalue")
    self.mixin.process_response(None, self.response)
    self.assertTrue(self.response.cookies[cookie_name]['secure'])
