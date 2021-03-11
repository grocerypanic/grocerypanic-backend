"""Ensure SameSite cookies are returned correctly to the user's browser."""

from django.conf import settings
from django.contrib.sessions.middleware import MiddlewareMixin

from ..cookies.samesite import SameSiteReWriter


class SameSiteMiddleware(MiddlewareMixin):
  """Middleware Mixin that rewrites SameSite cookie values correctly."""

  def process_response(self, _, response):
    """Process the incoming response object.

    Overrides:
    :func:`django.contrib.sessions.middleware.MiddlewareMixin.process_response`
    """

    csrf_cookie = SameSiteReWriter(
        settings.CSRF_COOKIE_NAME,
        "CSRF_COOKIE_SAMESITE",
        "CSRF_COOKIE_SECURE",
    )
    auth_cookie = SameSiteReWriter(
        settings.JWT_AUTH_COOKIE,
        "JWT_AUTH_COOKIE_SAMESITE",
        "REST_COOKIES_SECURE",
    )

    response = csrf_cookie.rewrite(response)
    response = auth_cookie.rewrite(response)
    return response
