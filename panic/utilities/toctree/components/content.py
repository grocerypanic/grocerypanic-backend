"""TocTree ReST content creation class."""

import os

from ..bases import AbstractContentGenerator


class TocTreeContent(AbstractContentGenerator):
  """Generates ReST content for a Sphinx TOC tree.

  :param logging_instance: A configured python logger
  :type logging_instance: :class:`logging.Logger`
  """

  python_extension = ".py"
  restructured_text_extension = ".rst"
  index_filename = 'index' + restructured_text_extension
  module_index = '__init__'

  generate_content_message = "Generating TOC tree expected_content ..."
  generate_module_content_prefix = "Generating expected_content for module: "
  generate_index_content_prefix = "Generating expected_content for index: "

  def __init__(self, logging_instance):
    super().__init__(logging_instance)
    self.content = {}

  def accept(self, tree_instance):
    """Accept a tree instance to generate ReST content for.

    :param tree_instance: A TOC Tree instance
    :type tree_instance: :class:`utilities.toctree.TocTree`
    """
    self.tree = tree_instance

  def generate(self):
    """Generate TOC tree file content for each reST file.

    :returns: A dictionary keyed by file name, containing the content.
    :rtype: dict
    """
    self.logger.info(self.generate_content_message)
    for folder_struct in self.tree.destination_structure:
      self._process_files_in_folder(folder_struct)
    return self.content

  def _process_files_in_folder(self, folder_struct):
    parsed_folder, _, parsed_files = folder_struct
    for file_name in parsed_files:
      name_with_path = os.path.join(parsed_folder, file_name)
      self.content[name_with_path] = self._generate_file_content(
          name_with_path, folder_struct
      )

  def _generate_file_content(self, file_name, folder_struct):
    if file_name.endswith(self.index_filename):
      return self._generate_index_content(file_name, folder_struct)
    return self._generate_module_content(file_name, folder_struct)

  def _generate_index_content(self, filename, folder_struct):
    parsed_folder, parsed_subfolders, _ = folder_struct
    name = os.path.basename(os.path.dirname(filename))
    module_name = self._generate_module_name(parsed_folder)

    self.logger.debug("%s%s", self.generate_index_content_prefix, name)

    content = list()
    content.append(f"{name}")
    content.append("=" * (len(name)))
    content.append(f".. automodule:: {module_name}")
    content.append("   :members:")
    content.append("")
    content.append(".. toctree::")
    content.append("   :glob:")
    content.append("")
    parsed_subfolders.sort()
    for folder in parsed_subfolders:
      content.append("   " + os.path.join(folder, "index.rst"))
    content.append("   *")

    return content

  def _generate_module_content(self, filename, folder_struct):
    parsed_folder, _, _ = folder_struct
    name = os.path.basename(os.path.splitext(filename)[0])
    module_name = self._generate_module_name(parsed_folder, name)

    self.logger.debug("%s%s", self.generate_module_content_prefix, name)

    content = list()
    content.append(f"{name}.py")
    content.append("=" * (len(name) + 3))
    content.append(f".. automodule:: {module_name}")
    content.append("   :members:")

    return content

  def _generate_module_name(self, folder_path, filename=""):
    if filename:
      filename = "." + filename
    module_path = self.tree.module_names[folder_path]
    return module_path + filename
