"""Kitchen Store Views"""

from rest_framework import mixins, viewsets

from spa_security.auth_cookie import CSRFMixin
from ..models.store import Store
from ..pagination import PagePaginationWithOverride
from ..serializers.store import StoreSerializer
from ..swagger import openapi_ready


class BaseStoreView(
    CSRFMixin,
):
  """Store Base API View"""
  serializer_class = StoreSerializer
  queryset = Store.objects.all()


class StoreViewSet(
    BaseStoreView,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
  """Store API View"""


class StoreListCreateViewSet(
    BaseStoreView,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Store List and Create API View"""
  pagination_class = PagePaginationWithOverride

  @openapi_ready
  def get_queryset(self):
    queryset = self.queryset
    return queryset.filter(user=self.request.user).order_by("index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new Store"""
    serializer.save(user=self.request.user)
