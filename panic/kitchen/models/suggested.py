"""SuggestedItem Model for AutoCompletion"""

from django.db import models

from spa_security.fields import BlondeCharField

MAX_LENGTH = 255


class SuggestedItem(models.Model):
  """Suggested Item Names used for AutoCompletion"""
  name = BlondeCharField(max_length=MAX_LENGTH, unique=True)

  objects = models.Manager()

  def __str__(self):
    return str(self.name)

  # pylint: disable=W0222
  def save(self, *args, **kwargs):
    self.full_clean()
    return super(SuggestedItem, self).save(*args, **kwargs)
