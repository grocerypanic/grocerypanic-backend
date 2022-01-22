"""Caching Decorators."""

from datetime import datetime
from typing import Any, Callable, Optional, Type, TypeVar, cast

from django.db.models import Model
from django.utils.timezone import now

SETTER_ERROR = "This attribute can not be assigned directly."

TypeFunctionReturn = TypeVar('TypeFunctionReturn')


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

  func: Callable[..., TypeFunctionReturn]

  def __init__(self, ttl_field: str, cached_field: Optional[str] = None):
    self.ttl_field = ttl_field
    self.cached_field = cached_field

  def __call__(
      self, func: Callable[..., TypeFunctionReturn]
  ) -> TypeFunctionReturn:
    """Configure the function, and return the configured decorator.

    :param func: The function to decorate with the persisting cache
    :type func: func

    :returns: A configured instance of the decorator
    :rtype: :class:`PersistentCachedProperty`
    """
    setattr(self, 'func', func)
    self._set_default_cached_field()
    return cast(TypeFunctionReturn, self)

  def _set_default_cached_field(self) -> None:
    if self.cached_field is None and self.func is not None:
      self.cached_field = "_" + self.func.__name__

  def __get__(
      self,
      instance: Model,
      cls: Optional[Type[Any]] = None
  ) -> TypeFunctionReturn:
    cache_value = cast(TypeFunctionReturn, getattr(instance, self.cached_field))
    ttl_value = cast(datetime, getattr(instance, self.ttl_field))

    if self._cache_is_valid(cache_value, ttl_value):
      return cache_value

    calculated_value: TypeFunctionReturn = self._write_cache(instance)
    self._save(instance, cache_value, calculated_value)

    return calculated_value

  def __delete__(self, instance: Model) -> None:
    self._write_cache(instance)

  def __set__(self, _instance: Model, _value: TypeFunctionReturn) -> None:
    raise AttributeError(SETTER_ERROR)

  def _cache_is_valid(
      self, cache_value: TypeFunctionReturn, ttl_value: datetime
  ) -> bool:
    if cache_value is not None:
      if self._ttl_is_valid(ttl_value):
        return True
    return False

  @staticmethod
  def _ttl_is_valid(ttl_value: datetime) -> bool:
    if ttl_value is not None and ttl_value > now():
      return True
    return False

  def _write_cache(self, instance: Model) -> TypeFunctionReturn:
    computed_value: TypeFunctionReturn = self.func(instance)
    setattr(instance, self.cached_field, computed_value)
    return computed_value

  @staticmethod
  def _save(
      instance: Model, cache_value: TypeFunctionReturn,
      calculated_value: TypeFunctionReturn
  ) -> None:
    if cache_value != calculated_value:
      instance.save()
