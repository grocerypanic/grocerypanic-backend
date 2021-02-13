"""Kitchen suggestion views."""

from rest_framework import mixins, viewsets

from ..models.suggested import SuggestedItem
from ..pagination import BasePagePagination
from ..serializers.suggested import SuggestedItemSerializer
from ..swagger import openapi_ready
from .bases import KitchenBaseView


class SuggestedBaseView(
    KitchenBaseView,
):
  """Suggestion base view."""

  queryset = SuggestedItem.objects.all().order_by("name")
  serializer_class = SuggestedItemSerializer


class SuggestedItemListViewSet(
    SuggestedBaseView,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Suggested items list view."""

  pagination_class = BasePagePagination

  @openapi_ready
  def get_queryset(self):
    """Retrieve the view queryset."""
    queryset = self.queryset
    return queryset.order_by("name")
