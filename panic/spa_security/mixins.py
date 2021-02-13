"""Custom security mixins."""

from django.conf import settings
from django.contrib.sessions.middleware import MiddlewareMixin
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect


class SameSiteMiddleware(MiddlewareMixin):
  """Comply with the latest standard for samesite cookies."""

  def __rewrite_cookie(self, cookie, samesite, secure):
    """Rewrite a http cookie with compliant information.

    :param cookie: A cookie object from a rest_framework response object
    :type cookie: :class:`django.http.SimpleCookie`
    :param samesite: The samesite django config for this cookie
    :type samesite: string, bool, None
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
    """Read a setting from the django config.

    :param setting_key: The key of the django setting to read
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
    """Read all config settings for a cookie.

    :param response: A rest_framework response object
    :type response: :class:`rest_framework.response.Response`
    :param cookie_name: The name of the cookie being processed
    :type cookie_name: str
    :param samesite_key: The settings key for this cookie's samesite setting
    :type samesite_key: str
    :param secure_key: The settings key for this cookie's secure setting
    :type secure_key: str

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
    """Process a django cookie to correct it if needed.

    :param response: A rest_framework response object
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
    """Process the incoming response object.

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
  """Ensure the endpoint performs CSRF validation, or returns an error."""

  @method_decorator(csrf_protect)
  def dispatch(self, *args, **kwargs):
    """Override the dispatch implementation in the view."""
    return super(CSRFMixin, self).dispatch(*args, **kwargs)
