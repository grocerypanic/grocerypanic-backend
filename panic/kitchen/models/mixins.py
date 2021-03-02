"""Mixins for Kitchen models."""

from django import forms
from django.core.exceptions import ValidationError

from . import constants


class FullCleanMixin:
  """Mixin class for Kitchen models, ensures full_clean is called on save."""

  # pylint: disable=signature-differs
  def save(self, *args, **kwargs):
    """Clean and save model."""
    self.full_clean()
    super().save(*args, **kwargs)


class RelatedFieldEnforcementMixin:
  """Mixin class for Kitchen models, enforces properties on related models."""

  def related_validator(self, related_fields, owner_field="user"):
    """Require the 'owner_field' of a related instance to match this instance.

    :param related_fields: The names of the related fields to check
    :type related_fields: List[str]
    :param owner_field: Must match on both related and current instances.
    :type owner_field: str

    :raises: :class:`django.core.exceptions.ValidationError`
    """
    errors = {owner_field: []}
    for related_field in related_fields:
      errors = self.__check_related_field(errors, related_field, owner_field)
    if errors[owner_field]:
      raise ValidationError(errors)

  def __check_related_field(self, errors, related_field, owner_field):
    instances = self.__get_instances(related_field)
    for instance in instances:
      if getattr(instance, owner_field) != getattr(self, owner_field):
        errors[related_field] = [
            f"This field must match the '{owner_field}' field."
        ]
        errors[owner_field] += [f"This must match the '{related_field}' field."]
    return errors

  def __get_instances(self, field_name):
    model = getattr(self.__class__, field_name).field.related_model
    pk = forms.model_to_dict(self)[field_name]
    instances = model.objects.filter(pk=pk)
    return instances


class UniqueNameConstraintMixin:
  """Mixin class for Kitchen models, uniqueness on names regardless of case."""

  def clean(self):
    """Validate the field `name` is unique regardless of case, per user.

    :raises: :class:`django.core.exceptions.ValidationError`
    """
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
