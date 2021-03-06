"""Test the TocTreeFactorySettings configuration."""

from django.test import TestCase

from utilities.toctree.settings import load_settings


class TestTocTreeFactorySettings(TestCase):
  """Test the TocTreeFactorySettings configuration."""

  def test_configured_toctree_settings(self):
    load_settings()
