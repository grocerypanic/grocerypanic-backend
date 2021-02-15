"""Tools to support OpenApi documentation."""

import functools

import pytz
from drf_yasg import openapi


def openapi_ready(func):
  """Decorate a view functions so that it is compatible with drf_yasg.

  Openapi generation needs to be able to call some methods on the viewset
  without a user on the request (or AnonymousUser being on it). drf_yasg sets
  the swagger_fake_view attr on the view when running these methods, so we can
  check for that and call the super method if it's present.

  :param func: An api view
  :type func: function
  :returns: The wrapped function with open api support
  :rtype: function
  """

  @functools.wraps(func)
  def wrapped(self, *args, **kwargs):
    if getattr(self, "swagger_fake_view", False):
      parent_class = self.__class__
      parent_class_instance = super(parent_class, self)
      function_name = func.__name__
      return getattr(parent_class_instance, function_name)(*args, **kwargs)
    return func(self, *args, **kwargs)

  return wrapped


custom_transaction_view_parm = openapi.Parameter(
    'history',
    openapi.IN_QUERY,
    description="the number of days to retrieve history for",
    type=openapi.TYPE_STRING,
    default=14
)

custom_item_consumption_view_parm = openapi.Parameter(
    'timezone',
    openapi.IN_QUERY,
    description="The timezone of the client",
    type=openapi.TYPE_STRING,
    default=pytz.utc.zone,
)
