"""Test the app engine app views."""

from unittest.mock import patch

from django.conf import settings
from django.test import TestCase

from .. import module_cache
from ..module_cache import warm_module_cache

MODULE_CACHE = module_cache.__name__


@patch(f"{MODULE_CACHE}.import_module")
class LoadInstalledAppsTest(TestCase):
  """Test the load_installed_apps function."""

  def test_load_installed_apps(self, m_import):
    warm_module_cache()
    m_import.assert_called()

    for app in settings.INSTALLED_APPS:
      for name in ('urls', 'views', 'models'):
        m_import.assert_any_call('%s.%s' % (app, name))

  def test_load_installed_apps_w_wrror(self, m_import):
    m_import.side_effect = ImportError
    warm_module_cache()

    for app in settings.INSTALLED_APPS:
      for name in ('urls', 'views', 'models'):
        m_import.assert_any_call('%s.%s' % (app, name))
