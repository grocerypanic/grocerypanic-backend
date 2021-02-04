"""Custom Authentication"""

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class JWTCookieAuthentication(JWTAuthentication):
  """Extends the authenticate functionality of
  :class:`rest_framework_simplejwt.authentication.JWTAuthentication`
  """

  def authenticate(self, request):
    """Determines if a request can proceed based on the presence of a valid JWT
    cookie.

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
