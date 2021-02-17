"""Item model managers."""

from django.db import models


class ExpirationManager(models.Manager):
  """Retrieve Inventory expiration data for individual items."""
