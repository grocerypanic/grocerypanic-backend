"""Pre-warm the module cache."""

from importlib import import_module

from django.conf import settings


def warm_module_cache():
  """Load all configured apps, warming the module cache."""
  for app in settings.INSTALLED_APPS:
    for name in ('urls', 'views', 'models'):
      try:
        import_module('%s.%s' % (app, name))
      except ImportError:
        pass
