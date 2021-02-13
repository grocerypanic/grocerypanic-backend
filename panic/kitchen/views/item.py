"""Kitchen item views."""

import pytz
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets
from rest_framework.response import Response

from ..filters import ItemFilter
from ..models.item import Item
from ..pagination import BasePagePagination
from ..serializers.item import ItemSerializer
from ..serializers.reports.item_consumption_history import (
    ItemConsumptionHistorySerializer,
)
from ..swagger import custom_item_consumption_view_parm, openapi_ready
from .bases import KitchenBaseView


class ItemBaseViewSet(
    KitchenBaseView,
):
  """Item base API view."""

  serializer_class = ItemSerializer
  queryset = Item.objects.all()


class ItemViewSet(
    ItemBaseViewSet,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
  """Item API view."""

  @openapi_ready
  def perform_update(self, serializer):
    """Update a Item."""
    serializer.save(user=self.request.user)


class ItemListCreateViewSet(
    ItemBaseViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Item list and create API view."""

  filter_backends = (filters.DjangoFilterBackend,)
  filterset_class = ItemFilter
  pagination_class = BasePagePagination

  @openapi_ready
  def get_queryset(self):
    """Retrieve the view queryset."""
    queryset = self.queryset
    return queryset.filter(user=self.request.user).order_by("index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new item."""
    serializer.save(user=self.request.user)


class ItemConsumptionHistoryViewSet(
    ItemBaseViewSet,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
  """Item consumption history API view."""

  serializer_class = ItemConsumptionHistorySerializer

  @openapi_ready
  @swagger_auto_schema(manual_parameters=[custom_item_consumption_view_parm])
  def retrieve(self, request, *args, **kwargs):
    """Retrieve a model instance."""
    timezone_query = self.request.GET.get('timezone', pytz.utc.zone)
    instance = self.get_object()
    serializer = self.get_serializer(
        instance,
        data={"timezone": timezone_query},
    )
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data)
