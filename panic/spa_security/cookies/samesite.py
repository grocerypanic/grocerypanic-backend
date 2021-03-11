"""Rewrite SameSite cookie details, ensuring fields are set properly."""

from django.conf import settings


class SameSiteReWriter:
  """Cookie rewriter, ensuring samesite fields are set correctly."""

  def __init__(self, cookie_name, samesite_key, secure_key):
    self.cookie_name = cookie_name
    self.samesite_key = samesite_key
    self.secure_key = secure_key

  def rewrite(self, response):
    """Rewrite the configured cookie in this response object.

    :param response: A rest_framework response object
    :type response: :class:`rest_framework.response.Response`

    :returns: The modified response
    :rtype: :class:`rest_framework.response.Response`
    """
    if self.cookie_name not in response.cookies:
      return response

    self._rewrite_cookie(response)
    return response

  def _rewrite_cookie(self, response):
    cookie = response.cookies[self.cookie_name]
    samesite = self._read_config_setting(self.samesite_key, None)
    secure = self._read_config_setting(self.secure_key, False)

    cookie['samesite'] = samesite
    if samesite is None:
      cookie['samesite'] = 'None'
    cookie['secure'] = secure
    return cookie

  def _read_config_setting(self, setting_key, default):
    return getattr(settings, setting_key, default)
