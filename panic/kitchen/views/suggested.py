"""Kitchen Suggestion Views"""

from rest_framework import mixins, viewsets

from ..models.suggested import SuggestedItem
from ..pagination import PagePagination
from ..serializers.suggested import SuggestedItemSerializer
from ..swagger import openapi_ready
from .bases import KitchenBaseView


class SuggestedBaseView(
    KitchenBaseView,
):
  """Suggestion Base View"""
  queryset = SuggestedItem.objects.all().order_by("name")
  serializer_class = SuggestedItemSerializer


class SuggestedItemListViewSet(
    SuggestedBaseView,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Suggested Items List View"""
  pagination_class = PagePagination

  @openapi_ready
  def get_queryset(self):
    queryset = self.queryset
    return queryset.order_by("name")
