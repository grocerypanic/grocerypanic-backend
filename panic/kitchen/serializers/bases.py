"""Base classes for custom serializers."""

from django.db.models import Model
from rest_framework import serializers

from ..exceptions import ValidationPermissionError
from .constants import UNIQUE_CONSTRAINT_MSG


class KitchenBaseModelSerializer(serializers.ModelSerializer):
  """Base class with methods to help validate permissions on related objects."""

  def __to_iterable(self, related_instance):
    """Convert the model instance into an iterable, if it is not already.

    :param related_instance: A django model instance being validated
    :type related_instance: :class:`django.db.models.Model`, List[
    :class:`django.db.models.Model`]

    :returns: A iterable version of the model, and a modifer string
    :rtype: List[:class:`django.db.models.Model`], str
    """
    if isinstance(related_instance, Model):
      return [related_instance], "a "
    return related_instance, ""

  def related_validator(self, related_instance, field, user_field="user"):
    """Require the 'user' field of a related instance to match request user.

    :param related_instance: A django model instance being validated
    :type related_instance: :class:`django.db.models.Model`,
      List[:class:`django.db.models.Model`]
    :param field: The field name storing the model that is being validated
    :type field: str
    :param user_field: The related instance's field that stores the user
    :type user_field: str

    :raises: :class:`rest_framework.exceptions.PermissionDenied`
    """
    iterable, modifier = self.__to_iterable(related_instance)
    for instance in iterable:
      if self.context['request'].user != getattr(instance, user_field):
        raise ValidationPermissionError(
            detail=f"Please provide {modifier}valid {field}.",
        )

  def case_unique_validator(self, value, field):
    """Require a field to be unique (regardless of case) per related user.

    :param value: The value being checked for case uniqueness
    :type value: str
    :param field: The model field being checked for case uniqueness
    :type field: str

    :raises: :class:`rest_framework.exceptions.ValidationError`
    """
    is_unchanged = (
        self.instance and value.lower() == getattr(self.instance, field).lower()
    )

    model = self.Meta.model
    user = self.context['request'].user
    query_filter = {f"{field}__iexact": value, "user": user}
    count = model.objects.filter(**query_filter).count()
    unique_limit = 1 if is_unchanged else 0

    if count > unique_limit:
      raise serializers.ValidationError(detail=UNIQUE_CONSTRAINT_MSG,)
