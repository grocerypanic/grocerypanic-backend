"""Inventory Transaction Model Managers"""

from django.db import models


class InventoryTransactionManager(models.Manager):
  """Provides Methods to Modify Inventory Based on Incoming Transaction"""

  def process(self, transaction):
    pass
