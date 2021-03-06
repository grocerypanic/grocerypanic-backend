"""TocTree writing tool."""

import os
import shutil

from ..bases import AbstractWriter


class TocTreeWriter(AbstractWriter):
  """Writes a TocTree instance to the file system, erasing all present data.

  :param logging_instance: A configured python logger
  :type logging_instance: :class:`logging.Logger`
  """

  erasing_message = "Destroying existing TOC Tree ..."
  writing_structure_message = "Writing virtual TOC Tree folders to disk ..."
  writing_content_message = "Writing virtual TOC Tree file content to disk ..."
  error_prefix = "ERROR: "

  def __init__(self, logging_instance):
    super().__init__(logging_instance)
    self.errors = []
    self.diff = {}

  def accept(self, tree_instance):
    """Accept a tree instance to write to disk.

    :param tree_instance: A TOC Tree instance
    :type tree_instance: :class:`utilities.toctree.TocTree`
    """
    self.tree = tree_instance

  def write(self):
    """Write a virtual TocTree instance to disk."""
    self._erase_existing()
    self._write_structure()
    self._write_content()

  def _erase_existing(self):
    self.logger.warning(self.erasing_message)
    shutil.rmtree(self.tree.root)

  def _write_structure(self):
    self.logger.info(self.writing_structure_message)
    for folder_struct in self.tree.destination_structure:
      folder, _, _ = folder_struct
      os.makedirs(folder, exist_ok=True)

  def _write_content(self):
    self.logger.info(self.writing_content_message)
    for file_name, content in self.tree.content.items():
      file_handle = open(file_name, "w")
      file_handle.write("\n".join(content))
