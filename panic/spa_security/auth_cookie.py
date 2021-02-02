"""Authentication and Mixins to Enable Cookie Based JWTs"""

from django.conf import settings
from django.contrib.sessions.middleware import MiddlewareMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
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


class SameSiteMiddleware(MiddlewareMixin):
  """Comply with the latest standard for samesite cookies."""

  def __rewrite_cookie(self, cookie, samesite, secure):
    """Rewrites a http cookie with compliant information.

    :param cookie: A cookie object from a Django response
    :type cookie: A Django Restframework Response Cookie Object
    :param samesite: The samesite django config for this cookie
    :type samesite: string, bool, none
    :param secure: The secure django config for this cookie
    :type secure: bool

    :returns: A rewritten cookie object
    :rtype: A Django Restframework Response Cookie Object
    """
    cookie['samesite'] = samesite
    if samesite is None:
      cookie['samesite'] = 'None'
    cookie['secure'] = secure
    return cookie

  def __read_config_setting(self, setting_key, default):
    """Reads a setting from the django config.

    :param setting_key: The key of the setting to read
    :type setting_key: string
    :param default: The default value to use if not configured
    :type setting_key: any

    :returns: The value of the key, or `default` accordingly
    """
    return getattr(settings, setting_key, default)

  def __read_cookie_config(
      self,
      response,
      cookie_name,
      samesite_key,
      secure_key,
  ):
    """Reads all config settings for a cookie..

    :param response: A Django Rest Framework Response Object
    :type response: :class:`rest_framework.response.Response`
    :param setting_key: The key of the setting to read
    :type setting_key: string
    :param default: The default value to use if not configured
    :type setting_key: any

    :returns: The value of the key, or `default` accordingly
    """
    samesite = self.__read_config_setting(samesite_key, None)
    secure = self.__read_config_setting(secure_key, False)
    return {
        "cookie": response.cookies[cookie_name],
        "samesite": samesite,
        "secure": secure,
    }

  def __process_cookie(self, response, cookie_name, samesite_key, secure_key):
    """Processes a Django cookie to correct if if needed.

    :param response: A Django Rest Framework Response Object
    :type response: :class:`rest_framework.response.Response`
    :param cookie_name: The cookie name to process
    :type cookie_name: string
    :param samesite_key: The django setting for this cookie's samesite config
    :type samesite_key: string
    :param secure_key: The django setting for this cookie's secure config
    :type secure_key: string

    :returns: The modified response object.
    :rtype: :class:`rest_framework.response.Response`
    """

    if cookie_name not in response.cookies:
      return response

    cookie_settings = self.__read_cookie_config(
        response, cookie_name, samesite_key, secure_key
    )

    self.__rewrite_cookie(**cookie_settings)
    return response

  def process_response(self, _, response):
    """Rewrites the response cookie values to ensure they are handled correctly
    by browsers implementing this standard.

    Overrides:
    :func:`django.contrib.sessions.middleware.MiddlewareMixin.process_response`
    """

    response = self.__process_cookie(
        response,
        settings.CSRF_COOKIE_NAME,
        "CSRF_COOKIE_SAMESITE",
        "CSRF_COOKIE_SECURE",
    )
    response = self.__process_cookie(
        response,
        settings.JWT_AUTH_COOKIE,
        "JWT_AUTH_COOKIE_SAMESITE",
        "REST_COOKIES_SECURE",
    )

    return response


class CSRFMixin:
  """Ensures the endpoint performs CSRF validation, or returns an error."""

  @method_decorator(csrf_protect)
  def dispatch(self, *args, **kwargs):
    return super(CSRFMixin, self).dispatch(*args, **kwargs)
