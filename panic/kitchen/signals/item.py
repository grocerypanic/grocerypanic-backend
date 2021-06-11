"""Handles signals from the Item model."""

from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from ..models.item import Item
from utilities.models.validators.m2m import ManyToManyRelatedValidator


@receiver(m2m_changed, sender=Item.preferred_stores.through)
def item_preferred_stores_validator(instance, pk_set, **kwargs):
  """Validate the preferred_stores m2m field's user relation."""
  if kwargs['action'] == 'pre_add':
    m2m_validator = ManyToManyRelatedValidator(
        related_field='preferred_stores',
        match_field='user',
    )
    m2m_validator.validate(instance, pk_set)
