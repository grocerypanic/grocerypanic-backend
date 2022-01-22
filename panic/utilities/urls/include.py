"""Utilities for importing urls."""

from types import ModuleType
from typing import List, Optional, Sequence, Tuple, Union, cast

from django.urls import URLPattern, URLResolver, include


class TypeIncludedModule(ModuleType):
  """Typed representation of an included UrlPattern module."""

  urlpatterns: "TypeUrlPatterns"


TypeUrlPatterns = Sequence[Union[URLResolver, URLPattern]]
TypeInclude = Tuple[TypeIncludedModule, Optional[str], Optional[str]]


def selective_include(
    module_name: str, blacklist: Sequence[str] = ()
) -> TypeInclude:
  """Filter :func:`django.urls.include` operations with a blacklist.

  :param module_name: The module to run :func:`django.urls.include` on
  :type module_name: str
  :param blacklist: A sequence of view names to NOT import
  :type blacklist: Sequence[str]
  """

  module = cast(TypeInclude, include(module_name))
  white_list: List[Union[URLResolver, URLPattern]] = list()

  for url in module[0].urlpatterns:
    if isinstance(url, URLPattern):
      if url.name in blacklist:
        continue
    white_list.append(url)

  module[0].urlpatterns = white_list

  return module
