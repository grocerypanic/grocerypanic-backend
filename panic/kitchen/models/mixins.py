"""Mixins for Kitchen models."""

from django.core.exceptions import ValidationError

from . import constants


class UniqueNameConstraintMixin:
  """Mixin class for Kitchen models, uniqueness on names regardless of case."""

  def clean(self):
    """Validate the field `name` is unique regardless of case, per user."""
    super().clean()
    count = self._meta.model.objects.\
        filter(
          name__iexact=self.name,
          user=self.user,
        ).exclude(
          id=self.id
        ).count()

    if count > 0:
      raise ValidationError(constants.UNIQUE_NAME_CONSTRAINT_ERROR)

  # pylint: disable=signature-differs
  def save(self, *args, **kwargs):
    """Clean and save model."""
    self.full_clean()
    super().save(*args, **kwargs)
