"""Views for the Item model."""

from datetime import datetime

from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import decorators, mixins, response, viewsets

from ..filters import ItemFilter
from ..models.item import Item
from ..pagination import BasePagePagination
from ..serializers.item import ItemSerializer
from ..serializers.reports.item_activity import ItemActivityReportSerializer
from ..swagger import openapi_ready
from .bases import KitchenBaseView
from utilities.views.deprecation import deprecated_warning


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

  @decorators.action(methods=["GET"], detail=True)
  def activity(self, request, *args, **kwargs):
    """Retrieve the activity report for an Item."""

    instance = self.get_object()
    serializer = ItemActivityReportSerializer(instance)
    return response.Response(serializer.data)


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
    return queryset.filter(user=self.request.user).order_by("_index")

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new item."""
    serializer.save(user=self.request.user)


class ItemActivityReportViewSet(
    ItemBaseViewSet,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
  """Item activity API view."""

  serializer_class = ItemActivityReportSerializer

  @swagger_auto_schema(deprecated=True)
  def retrieve(self, request, *args, **kwargs):
    """Retrieve the activity report for a Item.

    (Deprecated.)
    """

    sunset = datetime(year=2022, month=1, day=29)
    retrieve_response = super().retrieve(request, *args, **kwargs)
    return deprecated_warning(
        retrieve_response,
        sunset,
    )
