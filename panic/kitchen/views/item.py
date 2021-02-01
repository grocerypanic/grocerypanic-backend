"""Kitchen Item Views"""

from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets

from spa_security.auth_cookie import CSRFMixin
from ..filters import ItemFilter
from ..models.item import Item
from ..pagination import PagePagination
from ..serializers.item import ItemConsumptionHistorySerializer, ItemSerializer
from ..swagger import openapi_ready


class ItemBaseViewSet(
    CSRFMixin,
):
  """Item Base API View"""
  serializer_class = ItemSerializer
  queryset = Item.objects.all()


class ItemViewSet(
    ItemBaseViewSet,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
  """Item API View"""

  @openapi_ready
  def perform_update(self, serializer):
    """Update a Item"""
    serializer.save(user=self.request.user)


class ItemListCreateViewSet(
    ItemBaseViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Item List and Create API View"""
  filter_backends = (filters.DjangoFilterBackend,)
  filterset_class = ItemFilter
  pagination_class = PagePagination

  @openapi_ready
  def get_queryset(self):
    queryset = self.queryset
    return queryset.filter(user=self.request.user).order_by("index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new Item"""
    serializer.save(user=self.request.user)


class ItemConsumptionHistoryViewSet(
    CSRFMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
  """Item Consumption History API View"""
  serializer_class = ItemConsumptionHistorySerializer
  queryset = Item.objects.all()
