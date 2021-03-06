"""A Sphinx TocTree representation class."""


class TocTree:
  """Representation of a Sphinx TOC tree.

  :param destination_folder: Abs. path to the root of the destination location
  :type destination_folder: str
  :param validator_instance: An implementation of the validator abc
  :type validator_instance: :class:`utilities.toctree.bases.AbstractValidator`
  :param writer_instance: An implementation of the write abc
  :type writer_instance: :class:`utilities.toctree.bases.AbstractWriter`
  """

  def __init__(self, destination_folder, validator_instance, writer_instance):
    self.root = destination_folder
    self.validator = validator_instance
    self.writer = writer_instance
    self.module_names = {}
    self.source_structure = []
    self.destination_structure = []
    self.content = {}

  def validate(self):
    """Perform validation on the TocTree, and return the results.

    :returns: The validator object containing results
    :rtype: :class:`utilities.toctree.bases.AbstractValidator`
    """
    self.validator.accept(self)
    self.validator.validate()
    return self.validator

  def write(self):
    """Write a TocTree to disk, erasing existing content."""
    self.writer.accept(self)
    self.writer.write()
