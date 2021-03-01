"""Shelf model."""

from django.contrib.auth import get_user_model
from django.db import models
from naturalsortfield import NaturalSortField

from spa_security.fields import BlondeCharField

User = get_user_model()


class Shelf(models.Model):
  """Shelf model."""

  MAXIMUM_NAME_LENGTH = 255

  index = NaturalSortField(
      for_field="name",
      max_length=MAXIMUM_NAME_LENGTH,
  )  # Pagination Index
  name = BlondeCharField(max_length=MAXIMUM_NAME_LENGTH)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  objects = models.Manager()

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['user', 'name'], name='shelf per user')
    ]
    indexes = [
        models.Index(fields=['index']),
    ]
    verbose_name_plural = "Shelves"

  def __str__(self):
    return str(self.name)

  # pylint: disable=signature-differs
  def save(self, *args, **kwargs):
    """Clean and save model."""
    self.full_clean()
    super().save(*args, **kwargs)
