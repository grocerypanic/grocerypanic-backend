"""Handles signals from the Transaction model."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from ..models.inventory import Inventory


# pylint: disable = unused-argument
@receiver(post_save, sender='kitchen.Transaction')
def transaction_post_save_handler(instance, created, **kwargs):
  """Handle the Transaction model `post_save` signal."""
  if created:
    Inventory.objects.adjustment(instance)
