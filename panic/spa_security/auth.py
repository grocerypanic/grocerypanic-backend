"""Authentication classes for the rest_framework library."""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
  """Authentication that parses JWT tokens from cookies.

  Overrides: :class:`rest_framework_simplejwt.authentication.JWTAuthentication`

  The default `authenticate` class was throwing exceptions on some mangled
  headers.  This re-implementation resolves the issue.
  """

  def authenticate(self, request):
    """Validate requests based on the presence of a valid JWT cookie.

    Overrides:
    :func:`rest_framework_simplejwt.authentication.JWTAuthentication.
    authenticate`
    """
    cookie_name = getattr(settings, 'JWT_AUTH_COOKIE', None)
    raw_token = None

    if cookie_name:
      if cookie_name in request.COOKIES:
        raw_token = request.COOKIES.get(cookie_name)

    if not raw_token:
      return None

    validated_token = self.get_validated_token(raw_token)
    return self.get_user(validated_token), validated_token
