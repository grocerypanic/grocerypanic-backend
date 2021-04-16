"""Utilities for importing urls."""

from django.urls import include


def selective_include(module_name, blacklist=()):
  """Filter :func:`django.urls.include` operations with a blacklist.

  :param module_name: The module to run :func:`django.urls.include` on
  :type module_name: str
  :param blacklist: A list of view names to NOT import
  :type blacklist: List[str]
  """

  module = include(module_name)
  white_list = list()

  for url in module[0].urlpatterns:
    if url.name not in blacklist:
      white_list.append(url)

  module[0].urlpatterns = white_list

  return module
