"""Custom CSRF mixin."""

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect


class CSRFMixin:
  """Ensure the targeted view performs CSRF validation."""

  @method_decorator(csrf_protect)
  def dispatch(self, *args, **kwargs):
    """Override the dispatch implementation in the view."""
    return super().dispatch(*args, **kwargs)
