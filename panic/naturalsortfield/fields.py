"""Django field for natural sort ordering."""

import re

from django.db import models


class NaturalSortField(models.CharField):
  """Django field for natural sort ordering."""

  def __init__(self, for_field, **kwargs):
    self.for_field = for_field
    kwargs.setdefault('db_index', True)
    kwargs.setdefault('editable', False)
    kwargs.setdefault('max_length', 255)
    super().__init__(**kwargs)
    self.max_length = kwargs['max_length']

  def deconstruct(self):
    """Return enough information to recreate the field as a 4-tuple."""

    name, path, args, kwargs = super().deconstruct()
    args.append(self.for_field)
    return name, path, args, kwargs

  def pre_save(self, model_instance, add):
    """Return field's value just before saving."""

    return self.naturalize(getattr(model_instance, self.for_field))

  def naturalize(self, string):
    """Return a naturalized sortable version of the input string.

    :param string: The string value you wish to make naturalized sortable.
    :type string: str
    :returns: A naturalized sortable version of the input string.
    :rtype: string
    """

    def naturalize_int_match(match):
      return '%08d' % (int(match.group(0)),)

    string = string.lower()
    string = string.strip()
    string = re.sub(r'^the\s+', '', string)
    string = re.sub(r'\d+', naturalize_int_match, string)
    string = string[:self.max_length]

    return string
