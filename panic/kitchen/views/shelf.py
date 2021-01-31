"""Kitchen Shelf Views"""

from rest_framework import mixins, viewsets

from spa_security.auth_cookie import CSRFMixin
from ..models.shelf import Shelf
from ..pagination import PagePaginationWithOverride
from ..serializers.shelf import ShelfSerializer
from ..swagger import openapi_ready


class BaseShelfView(
    CSRFMixin,
):
  """Shelf Base API View"""
  serializer_class = ShelfSerializer
  queryset = Shelf.objects.all()


class ShelfViewSet(
    BaseShelfView,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
  """Shelf API View"""


class ShelfListCreateViewSet(
    BaseShelfView,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Shelf List and Create API View"""
  pagination_class = PagePaginationWithOverride

  @openapi_ready
  def get_queryset(self):
    queryset = self.queryset
    return queryset.filter(user=self.request.user).order_by("index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new Shelf"""
    serializer.save(user=self.request.user)
