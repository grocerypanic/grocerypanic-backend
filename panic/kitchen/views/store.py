"""Views for the Store model."""

from rest_framework import mixins, viewsets

from ..models.store import Store
from ..pagination import PagePaginationWithOverride
from ..serializers.store import StoreSerializer
from ..swagger import openapi_ready
from .bases import KitchenBaseView
from .mixins import ProtectedResourceMixin


class StoreBaseView(
    KitchenBaseView,
):
  """Store base API view."""

  serializer_class = StoreSerializer
  queryset = Store.objects.all()


class StoreViewSet(
    StoreBaseView,
    ProtectedResourceMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
  """Store API view."""


class StoreListCreateViewSet(
    StoreBaseView,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Store list and create API views."""

  pagination_class = PagePaginationWithOverride

  @openapi_ready
  def get_queryset(self):
    """Retrieve the view queryset."""
    queryset = self.queryset
    return queryset.filter(user=self.request.user).order_by("_index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new store."""
    serializer.save(user=self.request.user)
