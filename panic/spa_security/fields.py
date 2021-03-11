"""Django model fields for the spa_security app."""

from django.conf import settings
from django.db import models
from django_bleach.models import BleachField


class BlondeCharField(models.CharField, BleachField):
  """A django_bleach derived char field, with appropriate protection."""

  def pre_save(self, model_instance, add):
    """Override the :class:`django.db.models.fields.Field` `pre_save` hook.

    Allows for restoring some modified fields after they have been "bleached".
    """
    restored_data = None
    data = super().pre_save(model_instance, add)
    for key, value in getattr(settings, "BLEACH_RESTORE_LIST", {}).items():
      restored_data = data.replace(key, value)
    if restored_data:
      setattr(model_instance, self.attname, restored_data)
      return restored_data
    return data
