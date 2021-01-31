"""Kitchen Suggestion Views"""

from rest_framework import mixins, viewsets

from spa_security.auth_cookie import CSRFMixin
from ..models.suggested import SuggestedItem
from ..pagination import PagePagination
from ..serializers.suggested import SuggestedItemSerializer
from ..swagger import openapi_ready


class SuggestedItemListViewSet(
    CSRFMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Suggested Items List View"""
  serializer_class = SuggestedItemSerializer
  queryset = SuggestedItem.objects.all().order_by("name")
  pagination_class = PagePagination

  @openapi_ready
  def get_queryset(self):
    queryset = self.queryset
    return queryset.order_by("name")
