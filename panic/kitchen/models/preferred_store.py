"""PreferredStore model."""

from django.db import models


class PreferredStore(
    models.Model,
):
  """PreferredStore model."""

  item = models.ForeignKey(
      'kitchen.Item',
      on_delete=models.CASCADE,
  )
  store = models.ForeignKey(
      'kitchen.Store',
      on_delete=models.RESTRICT,
  )

  objects = models.Manager()

  def __str__(self):
    return str(f"{self.item}'s preferred store: {self.store}")
