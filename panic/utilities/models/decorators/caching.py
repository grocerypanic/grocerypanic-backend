"""Caching Decorators."""

from django.utils.timezone import now

SETTER_ERROR = "This attribute can not be assigned directly."


class PersistentCachedProperty:
  """Persistent implementation of the cached_property decorator.

  Specify another model field (storing a datetime) that can be used to
  act as a cache ttl, and an internal nullable field to hold the value
  persistently.

  Call `del` on the property to delete the cached value and replace it with
  up to date data.

  :param ttl_field: Model field containing a datetime to control TTL
  :type ttl_field: str
  :param cached_field: Model field to store the value (default: _ + field name)
  :type cached_field: str
  """

  def __init__(self, ttl_field, cached_field=None):
    self.func = None
    self.ttl_field = ttl_field
    self.cached_field = cached_field

  def __call__(self, func):
    """Configure the function, and return the configured decorator.

    :param func: The function to decorate with the persisting cache
    :type func: func

    :returns: A configured instance of the decorator
    :rtype: :class:`PersistentCachedProperty`
    """
    self.func = func
    self._set_default_cached_field()
    return self

  def _set_default_cached_field(self):
    if self.cached_field is None:
      self.cached_field = "_" + self.func.__name__

  def __get__(self, instance, cls=None):
    cache_value = getattr(instance, self.cached_field)
    ttl_value = getattr(instance, self.ttl_field)

    if self._cache_is_valid(cache_value, ttl_value):
      return cache_value

    calculated_value = self._write_cache(instance)
    self._save(instance, cache_value, calculated_value)

    return calculated_value

  def __delete__(self, instance):
    self._write_cache(instance)

  def __set__(self, _instance, _value):
    raise AttributeError(SETTER_ERROR)

  def _cache_is_valid(self, cache_value, ttl_value):
    if cache_value is not None:
      if self._ttl_is_valid(ttl_value):
        return True
    return False

  @staticmethod
  def _ttl_is_valid(ttl_value):
    if ttl_value is not None and ttl_value > now():
      return True
    return False

  def _write_cache(self, instance):
    computed_value = self.func(instance)
    setattr(instance, self.cached_field, computed_value)
    return computed_value

  @staticmethod
  def _save(instance, cache_value, calculated_value):
    if cache_value != calculated_value:
      instance.save()
