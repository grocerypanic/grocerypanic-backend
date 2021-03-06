"""Tests for the TocTreeFactorySettings class."""

from logging import Logger
from unittest import TestCase

from django.conf import settings
from django.test import override_settings

from .. import bases
from ..settings import (
    DJANGO_SETTINGS_NAME,
    TocTreeFactorySettings,
    load_settings,
)


class TestTocTreeFactorySettings(TestCase):
  """Test the TestTocTreeFactorySettings class."""

  def setUp(self):
    self.settings = TocTreeFactorySettings()

  def test_components(self):
    self.assertTrue(
        issubclass(self.settings.content, bases.AbstractContentGenerator),
    )
    self.assertTrue(isinstance(self.settings.logger, Logger))
    self.assertTrue(issubclass(self.settings.pruner, bases.AbstractPruner))
    self.assertTrue(
        issubclass(self.settings.validator, bases.AbstractValidator),
    )
    self.assertTrue(issubclass(self.settings.writer, bases.AbstractWriter))

  def test_configuration(self):
    self.assertIsInstance(self.settings.python_extension, str)
    self.assertIsInstance(self.settings.restructured_text_extension, str)
    self.assertIsInstance(self.settings.index_filename, str)
    self.assertIsInstance(self.settings.module_index_basename, str)

  def test_messages(self):
    self.assertIsInstance(self.settings.read_source_structure_message, str)
    self.assertIsInstance(self.settings.create_virtual_tree_message, str)
    self.assertIsInstance(self.settings.added_folder_prefix, str)

  def test_number_of_constants(self):
    variable_count = len(vars(TocTreeFactorySettings))

    self.assertEqual(
        variable_count,
        18,
    )


class TestLoadSettings(TestCase):
  """Test the load_settings function."""

  @override_settings()
  def test_loads_default(self):
    del settings.TOCTREE_FACTORY_SETTINGS
    loaded_settings = load_settings()
    self.assertTrue(isinstance(loaded_settings, TocTreeFactorySettings),)

  @override_settings(TOCTREE_FACTORY_SETTINGS="non_existent_module.settings")
  def test_loads_invalid(self):
    with self.assertRaises(ValueError) as raised:
      load_settings()
    self.assertEqual(
        raised.exception.args[0],
        (
            f"Django setting: {DJANGO_SETTINGS_NAME} is not an instance "
            "of TocTreeFactorySettings "
        ),
    )

  @override_settings(
      TOCTREE_FACTORY_SETTINGS="utilities.toctree.settings.default_settings"
  )
  def test_loads_valid(self):
    loaded_settings = load_settings()
    self.assertEqual(
        loaded_settings.__class__,
        TocTreeFactorySettings,
    )
