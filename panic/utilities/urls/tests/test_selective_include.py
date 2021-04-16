"""Test the selective_include function."""

import sys
from unittest import TestCase

from django.urls import include

from ...tests.fixtures import urlpatterns
from ..include import selective_include

MODULE_NAME = urlpatterns.__name__
del urlpatterns


class TestSelectiveInclude(TestCase):
  """Test the selective_include function."""

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.module_name = MODULE_NAME
    cls.all_urls = list(include(cls.module_name)[0].urlpatterns)

  def _get_urlpatterns(self, module):
    return module[0].urlpatterns

  def _patterns_equal(self, urlpatterns1, urlpatterns2):
    for index, url1 in enumerate(urlpatterns1):
      url2 = urlpatterns2[index]
      if url1.name != url2.name:
        return False
    return True

  def _pattern_missing(self, patterns, missing):
    for url in patterns:
      if url.name == missing:
        return False
    return True

  def setUp(self):
    sys.modules.pop(self.module_name)

  def test_import_all(self):
    result = selective_include(self.module_name)
    self.assertTrue(self._patterns_equal(result[0].urlpatterns, self.all_urls),)

  def test_filter_1(self):
    result = selective_include(self.module_name, blacklist=["test1"])
    self.assertFalse(
        self._patterns_equal(result[0].urlpatterns, self.all_urls),
    )

    self.assertTrue(self._pattern_missing(result[0].urlpatterns, "test1"),)
    self.assertFalse(self._pattern_missing(result[0].urlpatterns, "test2"),)
    self.assertFalse(self._pattern_missing(result[0].urlpatterns, "test3"),)

  def test_filter_1_and_3(self):
    result = selective_include(self.module_name, blacklist=["test1", "test3"])
    self.assertFalse(
        self._patterns_equal(result[0].urlpatterns, self.all_urls),
    )

    self.assertTrue(self._pattern_missing(result[0].urlpatterns, "test1"),)
    self.assertFalse(self._pattern_missing(result[0].urlpatterns, "test2"),)
    self.assertTrue(self._pattern_missing(result[0].urlpatterns, "test3"),)
