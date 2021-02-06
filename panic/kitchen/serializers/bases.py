"""Base classes for custom serializers."""

from django.db.models import Model
from rest_framework import serializers

from ..exceptions import ValidationPermissionError


class RelatedValidatorModelSerializer(serializers.ModelSerializer):
  """Model Serializer with helper method for validating related models are
  owned by the current user.
  """

  def __to_iterable(self, related_instance):
    """A helper function that converts any related_instance model to a iterable
    and returns a english particle to indicate if it's singular or not.

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
    """A helper function that can be called to ensure the 'user' field of any
    related instance being validated matches the current user.

    :param related_instance: A django model instance being validated
    :type related_instance: :class:`django.db.models.Model`, List[
    :class:`django.db.models.Model`]
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
