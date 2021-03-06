"""Test the TocTreeValidator class."""

import difflib
from unittest import TestCase
from unittest.mock import Mock, mock_open, patch

from ... import TocTree
from ...tests.fixtures.fixtures_toctree import (
    DESTINATION,
    DESTINATION_FILE_CONTENT,
)
from .. import validator as validator_module
from ..logging import logger
from ..validator import TocTreeValidator


class TestTocTreeValidation(TestCase):
  """Test the TocTreeValidator class."""

  def setUp(self):
    self.writer = Mock()
    self.validator = TocTreeValidator(logger)
    self.tree = TocTree(DESTINATION, self.validator, self.writer)
    self.tree.content = DESTINATION_FILE_CONTENT

  @patch(validator_module.__name__ + ".os.path.exists")
  def test_compare_not_existing(self, m_exists):
    m_exists.return_value = False
    self.validator.accept(self.tree)
    self.validator.validate()

    for file_name, _ in DESTINATION_FILE_CONTENT.items():
      self.assertIn(
          self.validator.generate_missing_file_error_message(file_name),
          self.validator.errors,
      )

  @patch(validator_module.__name__ + ".open", mock_open(read_data=""))
  @patch(validator_module.__name__ + ".os.path.exists")
  def test_compare_content_errors(self, m_exists):
    m_exists.return_value = True
    self.validator.accept(self.tree)
    self.validator.validate()

    for file_name, _ in DESTINATION_FILE_CONTENT.items():
      self.assertIn(
          self.validator.generate_content_error_message(file_name),
          self.validator.errors,
      )

  @patch(validator_module.__name__ + ".open", mock_open(read_data=""))
  @patch(validator_module.__name__ + ".os.path.exists")
  def test_compare_content_diff(self, m_exists):
    m_exists.return_value = True
    self.validator.accept(self.tree)
    self.validator.validate()

    for file_name, content in DESTINATION_FILE_CONTENT.items():
      self.assertIn(
          "\n".join(difflib.unified_diff([""], content)),
          self.validator.diff[
              self.validator.generate_content_error_message(file_name)],
      )

  @patch(validator_module.__name__ + ".open", mock_open(read_data=""))
  @patch(validator_module.__name__ + ".os.path.exists")
  def test_compare_content_same(self, m_exists):
    m_exists.return_value = True

    modified_file_content = dict(DESTINATION_FILE_CONTENT)
    mock_file = f"{DESTINATION}/folder3/folder4/file4b.rst"
    modified_file_content[mock_file] = [""]
    self.tree.content[mock_file] = [""]

    self.validator.accept(self.tree)
    self.validator.validate()

    for file_name, content in modified_file_content.items():
      if file_name != mock_file:
        self.assertIn(
            "\n".join(difflib.unified_diff([""], content)),
            self.validator.diff[
                self.validator.generate_content_error_message(file_name)],
        )
