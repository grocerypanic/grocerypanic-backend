"""Views for the Item model."""

from django_filters import rest_framework as filters
from rest_framework import decorators, mixins, response, viewsets

from ..filters import ItemFilter
from ..models.item import Item
from ..pagination import BasePagePagination
from ..serializers.item import ItemSerializer
from ..serializers.reports.item_activity import ItemActivityReportSerializer
from ..swagger import openapi_ready
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
    """Update an Item."""
    serializer.save(user=self.request.user)

  @decorators.action(methods=["GET"], detail=True)
  def activity(self, *args, **kwargs):  # pylint: disable=unused-argument
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
