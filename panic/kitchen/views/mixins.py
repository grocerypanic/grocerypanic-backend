"""Kitchen view Mixins."""

from django.db.models import RestrictedError

from ..exceptions import ResourceIsRequired


class ProtectedResourceMixin:
  """Handles RestrictedErrors on attempts to delete required resources."""

  def perform_destroy(self, instance):
    """Override perform_destroy."""
    try:
      return super().perform_destroy(instance)
    except RestrictedError as exc:
      raise ResourceIsRequired from exc
