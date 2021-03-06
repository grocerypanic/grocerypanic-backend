"""TocTree validation tool."""

import difflib
import os

from .. import bases


class TocTreeValidator(bases.AbstractValidator):
  """Validation of TocTree instances against the file system.

  Validates whether the expected TOC Tree structure and expected_content
  matches the file system.

  :param logging_instance: A configured python logger
  :type logging_instance: :class:`logging.Logger`
  """

  comparing_message = "Comparing virtual TOC Tree to actual ..."
  error_prefix = "ERROR: "
  error_missing_suffix = " ... missing."
  error_content_suffix = " ... content is different."

  def __init__(self, logging_instance):
    super().__init__(logging_instance)
    self.errors = []
    self.diff = {}

  def accept(self, tree_instance):
    """Accept a tree instance to perform validation on.

    :param tree_instance: A TOC Tree instance
    :type tree_instance: :class:`utilities.toctree.TocTree`
    """
    self.tree = tree_instance

  def validate(self):
    """Compare a virtual TocTree instance against the expected actual tree."""
    self.logger.info(self.comparing_message)
    for file_name, content in self.tree.content.items():
      if self.check_file_exists(file_name):
        self.check_content(file_name, content)

  def check_file_exists(self, file_name):
    """Check a TocTree file exists, and report an error if it does not.

    :param file_name: A TocTree file with absolute path
    :type file_name: str

    :returns: A boolean indicating if the file exists.
    :rtype: bool
    """
    exists = os.path.exists(file_name)
    if not exists:
      message = self.generate_missing_file_error_message(file_name)
      self.logger.error(message)
      self.errors.append(message)
    return exists

  def check_content(self, file_name, expected_content):
    """Check a TocTree file's content is correct, and report an error if not.

    :param file_name: A TocTree file with absolute path
    :type file_name: str
    :param expected_content: A string containing the expected file contents
    :type expected_content: str
    """
    with open(file_name) as fhandle:
      existing_content = fhandle.read().split("\n")
      if existing_content != expected_content:
        message = self.generate_content_error_message(file_name)
        self.logger.error(message)
        self.errors.append(message)
        self.diff[message] = "\n".join(
            difflib.unified_diff(existing_content, expected_content)
        )

  def generate_missing_file_error_message(self, file_name):
    """Generate a missing file error message based on file_name.

    :param file_name: A TocTree file with absolute path
    :type file_name: str

    :returns: A string containing error message
    :rtype: str
    """
    return f"{self.error_prefix}{file_name}{self.error_missing_suffix}"

  def generate_content_error_message(self, file_name):
    """Generate a content error message based on file_name.

    :param file_name: A TocTree file with absolute path
    :type file_name: str

    :returns: A string containing error message
    :rtype: str
    """
    return f"{self.error_prefix}{file_name}{self.error_content_suffix}"
