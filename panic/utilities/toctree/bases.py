"""Bases for Sphinx TocTree validation/generation."""

import abc
from logging import Logger
from typing import Type

from . import TocTree


class AbstractVisitor(abc.ABC):
  """Abstract base class for a TocTree visitor class."""

  tree: TocTree

  @abc.abstractmethod
  def accept(self, tree_instance):
    """Abstract `accept` method.

    :param tree_instance: A TocTree instance
    :type tree_instance: :class:`utilities.toctree.TocTree`
    """


class AbstractPruner(AbstractVisitor):
  """Abstract base class for a TocTree pruner.

  :param source_folder: Abs. path to the code base root
  :type source_folder: str
  """

  def __init__(self, source_folder):
    self.source_folder = source_folder

  @abc.abstractmethod
  def prune(self, settings):
    """Abstract `pruner` method.

    :param settings: A TocTreeFactorySettings instance
    :type settings: :class:`utilities.toctree.factory.TocTreeFactorySettings`
    """


class AbstractContentGenerator(AbstractVisitor):
  """Abstract base class for a TocTree content generator.

  :param logging_instance: A configured python logger
  :type logging_instance: :class:`logging.Logger`
  """

  def __init__(self, logging_instance):
    self.logger = logging_instance

  @abc.abstractmethod
  def generate(self):
    """Abstract `generate` method."""


class AbstractValidator(AbstractVisitor):
  """Abstract base class for a TocTree validator.

  :param logging_instance: A configured python logger
  :type logging_instance: :class:`logging.Logger`
  """

  errors: list
  diff: dict

  def __init__(self, logging_instance):
    self.logger = logging_instance

  @abc.abstractmethod
  def validate(self):
    """Abstract `validate` method."""


class AbstractWriter(AbstractVisitor):
  """Abstract base class for a TocTree writer.

  :param logging_instance: A configured python logger
  :type logging_instance: :class:`logging.Logger`
  """

  def __init__(self, logging_instance):
    self.logger = logging_instance

  @abc.abstractmethod
  def write(self):
    """Abstract `write` method."""


class AbstractTocTreeFactorySettings(abc.ABC):
  """Abstract base class for TocTree settings."""

  read_source_structure_message: str
  create_virtual_tree_message: str
  added_folder_prefix: str

  python_extension: str
  restructured_text_extension: str
  index_filename: str
  module_index_basename: str

  content: Type[AbstractContentGenerator]
  logger: Logger
  pruner: Type[AbstractPruner]
  validator: Type[AbstractValidator]
  writer: Type[AbstractWriter]

  files_filter_list: list
  folders_filter_list: list
