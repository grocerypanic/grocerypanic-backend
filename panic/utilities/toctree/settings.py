"""Configuration for the TocTreeFactory class."""

from pydoc import locate

from django.conf import settings

from .bases import AbstractTocTreeFactorySettings
from .components import content, logging, pruner, validator, writer

DJANGO_SETTINGS_NAME = 'TOCTREE_FACTORY_SETTINGS'


class TocTreeFactorySettings(AbstractTocTreeFactorySettings):
  """Configuration for creating TocTree instances."""

  read_source_structure_message = "Reading codebase structure ..."
  create_virtual_tree_message = "Building virtual TOC Tree ..."
  added_folder_prefix = "added: "

  python_extension = ".py"
  restructured_text_extension = ".rst"
  index_filename = 'index' + restructured_text_extension
  module_index_basename = '__init__'

  content = content.TocTreeContent
  logger = logging.logger
  pruner = pruner.TocTreePruner
  validator = validator.TocTreeValidator
  writer = writer.TocTreeWriter

  files_filter_list = ['manage.py']
  folders_filter_list = [
      '__pycache__',
      'fixtures',
      'migrations',
      'static',
      'tests',
  ]


def load_settings() -> TocTreeFactorySettings:
  """Load configured TocTreeFactorySettings instance, or default settings."""

  factory_settings_library = getattr(
      settings,
      DJANGO_SETTINGS_NAME,
      None,
  )
  if factory_settings_library:
    loaded_settings = locate(factory_settings_library)
    if isinstance(loaded_settings, TocTreeFactorySettings):
      return loaded_settings
    raise ValueError(
        f"Django setting: {DJANGO_SETTINGS_NAME} is not an instance "
        "of TocTreeFactorySettings "
    )
  return default_settings


default_settings = TocTreeFactorySettings()
