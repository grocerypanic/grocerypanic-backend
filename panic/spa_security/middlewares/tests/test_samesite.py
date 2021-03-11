"""Test the custom samesite middleware mixin."""

from unittest.mock import Mock, call, patch

from django.conf import settings
from django.http import HttpResponse
from django.test import SimpleTestCase

from .. import samesite as middleware_module
from ..samesite import SameSiteMiddleware

MIDDLEWARE_MODULE = middleware_module.__name__


@patch(MIDDLEWARE_MODULE + ".SameSiteReWriter")
class TestSameSiteMiddleware(SimpleTestCase):
  """Test the SameSiteMiddleware class."""

  def setUp(self):
    self.response = HttpResponse()
    self.mixin = SameSiteMiddleware()

  def test_initializes_rewriter(self, m_rewriter):
    self.mixin.process_response(None, self.response)

    csrf_call = call(
        settings.CSRF_COOKIE_NAME,
        "CSRF_COOKIE_SAMESITE",
        "CSRF_COOKIE_SECURE",
    )
    jwt_call = call(
        settings.JWT_AUTH_COOKIE,
        "JWT_AUTH_COOKIE_SAMESITE",
        "REST_COOKIES_SECURE",
    )

    m_rewriter.asset_has_calls(csrf_call, jwt_call)
    self.assertEqual(
        m_rewriter.call_count,
        2,
    )

  def test_rewriter_instances_are_called(self, m_rewriter):
    mock_instance = Mock()
    m_rewriter.return_value = mock_instance
    mock_instance.rewrite.side_effect = [
        "after_process_first_cookie", "after_process_second_cookie"
    ]

    return_value = self.mixin.process_response(None, self.response)

    process_first_cookie = call(self.response)
    process_second_cookie = call("after_process_first_cookie")

    m_rewriter.asset_has_calls(process_first_cookie, process_second_cookie)

    self.assertEqual(
        return_value,
        "after_process_second_cookie",
    )
