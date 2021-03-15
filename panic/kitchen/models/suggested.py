"""SuggestedItem model."""

from django.db import models

from spa_security.fields import BlondeCharField
from .mixins import FullCleanMixin


class SuggestedItem(
    FullCleanMixin,
    models.Model,
):
  """SuggestItem model."""

  MAXIMUM_NAME_LENGTH = 255

  name = BlondeCharField(max_length=MAXIMUM_NAME_LENGTH, unique=True)

  objects = models.Manager()

  def __str__(self):
    return str(self.name)
