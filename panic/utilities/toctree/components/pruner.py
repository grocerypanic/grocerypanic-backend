"""Pruner class for transforming a generated filesystem into TocTree data."""

import os

from ..bases import AbstractPruner, AbstractTocTreeFactorySettings


class TocTreePruner(AbstractPruner):
  """Prune and transform generated filesystem, into writable TocTree data.

  :param source_folder: Abs. path to the code base root
  :type source_folder: str
  """

  settings: AbstractTocTreeFactorySettings

  def __init__(self, source_folder):
    super().__init__(source_folder)
    self.pruned_module_names = {}
    self.pruned_file_system = []

  def accept(self, tree_instance):
    """Accept a tree instance to generate ReST content for.

    :param tree_instance: A TOC Tree instance
    :type tree_instance: :class:`utilities.toctree.TocTree`
    """
    self.tree = tree_instance

  def prune(self, settings):
    """Prune a TocTree, according to the received settings object.

    :param settings: A TocTreeFactorySettings instance
    :type settings: :class:`utilities.toctree.factory.TocTreeFactorySettings`
    """
    self.settings = settings
    self._prune_toctree()
    return self

  def _prune_toctree(self):
    pruned_folder_structure = self._prune_toctree_folder_structure()
    for folder_struct in pruned_folder_structure:
      new_folder_struct = self._generate_folder_contents(folder_struct)
      self.settings.logger.debug(
          "%s%s", self.settings.added_folder_prefix, new_folder_struct[0]
      )
      self.pruned_file_system.append(new_folder_struct)

  def _prune_toctree_folder_structure(self):
    pruned_file_system = []
    for folder_struct in self.tree.source_structure:
      pruned_files_struct = self._prune_toctree_files(folder_struct)
      pruned_folders_struct = self._prune_toctree_folders(pruned_files_struct)
      if pruned_folders_struct:
        pruned_subfolders_struct = self._prune_toctree_subfolders(
            pruned_folders_struct
        )
        pruned_file_system.append(pruned_subfolders_struct)
    return pruned_file_system

  def _prune_toctree_files(self, folder_struct):
    pruned_files = []
    parsed_folder, parsed_subfolders, parsed_files = folder_struct
    parsed_files = self._ensure_top_level_index(parsed_folder, parsed_files)
    for file_name in parsed_files:
      full_name = os.path.join(parsed_folder, file_name)
      if full_name in self.settings.files_filter_list:
        continue
      pruned_files.append(file_name)
    return parsed_folder, parsed_subfolders, pruned_files

  def _ensure_top_level_index(self, parsed_folder, parsed_files):
    if parsed_folder == self.source_folder:
      if "__init__.py" not in parsed_files:
        parsed_files.append("__init__.py")
    return parsed_files

  def _prune_toctree_folders(self, folder_struct):
    parsed_folder, parsed_subfolders, parsed_files = folder_struct
    if os.path.basename(parsed_folder) in self.settings.folders_filter_list:
      return []
    destination_folder = self._create_destination_folder(parsed_folder)
    self._add_folder_as_module(destination_folder)
    return destination_folder, parsed_subfolders, parsed_files

  def _prune_toctree_subfolders(self, folder):
    parsed_folder, parsed_subfolders, parsed_files = folder
    for filter_folder in self.settings.folders_filter_list:
      if filter_folder in parsed_subfolders:
        parsed_subfolders.remove(filter_folder)
    return parsed_folder, parsed_subfolders, parsed_files

  def _create_destination_folder(self, folder_path):
    destination_path_suffix = folder_path[len(self.source_folder):]
    destination_path = self.tree.root + destination_path_suffix
    return destination_path

  def _add_folder_as_module(self, destination_folder_path):
    module_name = destination_folder_path[len(self.tree.root) + 1:]
    if not module_name:
      module_name = os.path.basename(self.source_folder)
    module_name = module_name.split('/')
    self.pruned_module_names[destination_folder_path] = '.'.join(module_name)

  def _generate_folder_contents(self, folder_struct):
    parsed_folder, parsed_subfolders, parsed_files = folder_struct
    new_files = self._generate_folder_filenames(parsed_files)
    new_folder_struct = parsed_folder, parsed_subfolders, new_files
    return new_folder_struct

  def _generate_folder_filenames(self, parsed_files):
    new_files = []
    for parsed_file in parsed_files:
      name, ext = os.path.splitext(parsed_file)
      if ext == self.settings.python_extension:
        name = name if name != self.settings.module_index_basename else "index"
        extension = self.settings.restructured_text_extension
        new_files.append(f"{name}{extension}")
    return new_files
