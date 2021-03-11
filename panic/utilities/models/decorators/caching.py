"""Caching Decorators."""

from django.utils.timezone import now

SETTER_ERROR = "This attribute can not be assigned directly."


class PersistentCachedProperty:
  """Persisting version of the cached_property decorator.

  Generates a decorator for a model method with the PersistentCachedProperty
  class.  Specify another model field (storing a datetime) that can be used to
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
    self.ttl_field = ttl_field
    self.cached_field = cached_field

  def __call__(self, func):
    """Return the PersistentModelFieldCache."""
    return PersistentModelFieldCache(func, self.ttl_field, self.cached_field)


class PersistentModelFieldCache:
  """Persistent implementation of the cached_property decorator."""

  def __init__(self, func, ttl_field, cached_field=None):
    self.func = func
    self.ttl_field = ttl_field
    self.cached_field = self._get_cached_field(cached_field)

  def _get_cached_field(self, cached_field):
    if cached_field is None:
      return "_" + self.func.__name__
    return cached_field

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

  # pylint: disable=unused-argument
  def __set__(self, instance, value):
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
