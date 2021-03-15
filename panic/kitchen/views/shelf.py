"""Views for the Shelf model."""

from rest_framework import mixins, viewsets

from ..models.shelf import Shelf
from ..pagination import PagePaginationWithOverride
from ..serializers.shelf import ShelfSerializer
from ..swagger import openapi_ready
from .bases import KitchenBaseView


class BaseShelfView(
    KitchenBaseView,
):
  """Shelf base API view."""

  serializer_class = ShelfSerializer
  queryset = Shelf.objects.all()


class ShelfViewSet(
    BaseShelfView,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
  """Shelf API view."""


class ShelfListCreateViewSet(
    BaseShelfView,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Shelf list and create API view."""

  pagination_class = PagePaginationWithOverride

  @openapi_ready
  def get_queryset(self):
    """Retrieve the view queryset."""
    queryset = self.queryset
    return queryset.filter(user=self.request.user).order_by("_index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new shelf."""
    serializer.save(user=self.request.user)
