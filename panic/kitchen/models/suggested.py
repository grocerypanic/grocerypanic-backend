"""Suggested Item model."""

from django.db import models

from spa_security.fields import BlondeCharField


class SuggestedItem(models.Model):
  """Suggest Item model."""

  MAXIMUM_NAME_LENGTH = 255

  name = BlondeCharField(max_length=MAXIMUM_NAME_LENGTH, unique=True)

  objects = models.Manager()

  def __str__(self):
    return str(self.name)

  # pylint: disable=signature-differs
  def save(self, *args, **kwargs):
    """Clean and save model."""
    self.full_clean()
    return super(SuggestedItem, self).save(*args, **kwargs)
