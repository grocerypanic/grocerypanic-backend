"""Custom validators for Kitchen models."""

from django.core.exceptions import ValidationError


class ManyToManyValidator:
  """Validator for Many to Many fields.

  This validator checks that a named field matches on both an instance, and
  each related model in the M2M collection.

  :param related_field: A field on the instance that is the M2M to examine
  :type related_field: str
  :param match_field: A field that should match on instance and M2M collection
  :type match_field: str
  """

  def __init__(self, related_field=None, match_field=None):
    self.related_field = related_field
    self.match_field = match_field

  def validate(self, instance, pk_set):
    """Perform validation on a many to many field.

    :param instance: A model instance that has a M2M field to validate
    :type instance: :class:`django.db.models.Model`
    :param pk_set: A set of private key values for the m2m model
    :type pk_set: set(int)

    :raises: :class:`django.core.exceptions.ValidationError`
    """

    model = self._get_related_model(instance)
    related_instances = model.objects.filter(pk__in=pk_set)
    errors = self._collect_errors(instance, related_instances)

    if errors[self.match_field]:
      raise ValidationError(errors)

  def _get_related_model(self, instance):
    field = getattr(instance.__class__, self.related_field).field
    return field.related_model

  def _collect_errors(self, instance, related_instances):
    errors = {self.match_field: []}
    for related in related_instances:
      instance_value = self.get_instance_value(instance)
      related_value = self.get_related_value(related)
      if instance_value != related_value:
        errors[self.related_field] = [
            f"These selections must match the '{self.match_field}' field.",
        ]
        errors[self.match_field] += [
            f"This must match the '{self.related_field}' field.",
        ]
    return errors

  def get_instance_value(self, instance):
    """Return the value of the instance's match_field.

    :param instance: A model instance
    :type instance: :class:`django.db.models.Model`

    :returns: The value of the associated field.
    """
    return getattr(instance, self.match_field)

  def get_related_value(self, related_instance):
    """Return the value of the related_instances's match_field.

    :param related_instance: A related model instance
    :type related_instance: :class:`django.db.models.Model`

    :returns: The value of the associated field.
    """
    return getattr(related_instance, self.match_field)
