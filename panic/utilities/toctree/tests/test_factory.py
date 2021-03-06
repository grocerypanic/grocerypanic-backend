"""Tests for the TocTreeFactory class."""

from unittest import TestCase
from unittest.mock import Mock, patch

from .. import factory as factory_module
from ..factory import TocTreeFactory
from ..settings import TocTreeFactorySettings
from .fixtures.fixtures_toctree import (
    DESTINATION,
    DESTINATION_FILE_SYSTEM,
    SOURCE,
    SOURCE_FILE_SYSTEM,
)


class Settings(TocTreeFactorySettings):
  """Configured TocTreeFactorySettings for test."""

  files_filter_list = [f"{SOURCE}/folder1/manage.py"]


class TestTocTreeGenerator(TestCase):
  """Test the TocTreeFactory class."""

  def setUp(self):
    self.factory = TocTreeFactory(SOURCE, DESTINATION, Settings())

  @patch(factory_module.__name__ + ".os.walk")
  def test_built_root(self, m_walk):
    m_walk.return_value = SOURCE_FILE_SYSTEM
    instance = self.factory.build()

    self.assertEqual(
        instance.root,
        DESTINATION,
    )

  @patch(factory_module.__name__ + ".os.walk")
  def test_built_source_file_system(self, m_walk):
    m_walk.return_value = SOURCE_FILE_SYSTEM
    instance = self.factory.build()

    self.assertEqual(
        instance.source_structure,
        SOURCE_FILE_SYSTEM,
    )

  @patch(factory_module.__name__ + ".os.walk")
  def test_built_destination_file_system(self, m_walk):
    m_walk.return_value = SOURCE_FILE_SYSTEM

    instance = self.factory.build()

    self.assertEqual(
        instance.destination_structure,
        DESTINATION_FILE_SYSTEM,
    )

  @patch(factory_module.__name__ + ".os.walk")
  @patch(factory_module.__name__ + ".TocTreeFactorySettings.content")
  def test_rst_content_generated(self, m_content, m_walk):
    m_content_instance = Mock()
    m_walk.return_value = SOURCE_FILE_SYSTEM
    m_content.return_value = m_content_instance

    instance = self.factory.build()
    m_content.assert_called_once_with(self.factory.logger)
    m_content_instance.accept.assert_called_once_with(instance)
    m_content_instance.generate.assert_called_once_with()
