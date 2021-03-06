"""Generates TOCTree class instances from the file system."""

import os

from . import TocTree
from .settings import TocTreeFactorySettings

config = TocTreeFactorySettings()


class TocTreeFactory:
  """Factory for the class :class:`utilities.toctree.TocTree`.

  :param source_folder: Abs. path to the code base root
  :type source_folder: str
  :param destination_folder: Abs. path to the Sphinx source folder location
  :type destination_folder: str
  :param settings: An instance of TocTreeFactorySettings
  :type settings: :class:`utilities.toctree.settings.TocTreeFactorySettings`
  """

  def __init__(self, source_folder, destination_folder, settings):
    self.source_folder = source_folder
    self.destination_folder = destination_folder
    self.settings = settings
    self.logger = self.settings.logger
    self.tree = self._create_virtual_tree()

  def _create_virtual_tree(self):
    validator = self.settings.validator(self.logger)
    writer = self.settings.writer(self.logger)
    return TocTree(self.destination_folder, validator, writer)

  def build(self):
    """Build a new TocTree instance from the local filesystem.

    :returns: A configured TocTree instance
    :rtype: :class:`utilities.toctree.TocTree`
    """
    self._read_source_structure()
    self._prune_virtual_tree()
    self._create_virtual_tree_content()
    return self.tree

  def _read_source_structure(self):
    self.logger.info(self.settings.read_source_structure_message)
    for result in os.walk(self.source_folder):
      self.tree.source_structure.append(result)

  def _prune_virtual_tree(self):
    self.logger.info(self.settings.create_virtual_tree_message)
    pruned_data = self._prune_toc_tree()
    self.tree.module_names = pruned_data.pruned_module_names
    self.tree.destination_structure = pruned_data.pruned_file_system

  def _prune_toc_tree(self):
    pruner = self.settings.pruner(self.source_folder)
    pruner.accept(self.tree)
    pruned_data = pruner.prune(self.settings)
    return pruned_data

  def _create_virtual_tree_content(self):
    content_source = self.settings.content(self.logger)
    content_source.accept(self.tree)
    self.tree.content = content_source.generate()
