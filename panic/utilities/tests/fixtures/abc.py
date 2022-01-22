"""Utilities for testing abstract base classes."""

import abc
from typing import Any, Type


def concretor(abc_class: Type[abc.ABC]) -> Type[Any]:
  """Provide access to abc methods, to allow change detection in unittests.

  :param abc_class: An abstract base class
  :type abc_class: :class:`abc.ABC`

  :returns: A class inheriting the abstract methods directly
  :rtype: class
  """

  class ConcreteClass(abc_class):  # type: ignore
    pass

  ConcreteClass.__abstractmethods__ = frozenset()
  return type('DummyConcrete' + abc_class.__name__, (ConcreteClass,), {})
