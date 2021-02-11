"""User Shelf Model"""

from django.contrib.auth import get_user_model
from django.db import models
from naturalsortfield import NaturalSortField

from spa_security.fields import BlondeCharField

User = get_user_model()

MAX_LENGTH = 255


class Shelf(models.Model):
  """User Shelf Model"""
  index = NaturalSortField(
      for_field="name",
      max_length=MAX_LENGTH,
  )  # Pagination Index
  name = BlondeCharField(max_length=MAX_LENGTH)
  user = models.ForeignKey(User, on_delete=models.CASCADE)

  objects = models.Manager()

  class Meta:
    constraints = [
        models.UniqueConstraint(fields=['user', 'name'], name='shelf per user')
    ]
    indexes = [
        models.Index(fields=['index']),
    ]

  def __str__(self):
    return str(self.name)

  # pylint: disable=W0222
  def save(self, *args, **kwargs):
    self.full_clean()
    return super(Shelf, self).save(*args, **kwargs)
