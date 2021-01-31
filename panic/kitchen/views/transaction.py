"""Kitchen Transaction Views"""

import datetime

from django.conf import settings
from django.utils import timezone
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, viewsets

from spa_security.auth_cookie import CSRFMixin
from ..filters import TransactionFilter
from ..models.item import Item
from ..models.transaction import Transaction
from ..serializers.transaction import (
    TransactionConsumptionHistorySerializer,
    TransactionSerializer,
)
from ..swagger import custom_transaction_view_parm, openapi_ready


class TransactionViewSet(
    CSRFMixin,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
  """Transaction API View"""
  serializer_class = TransactionSerializer
  queryset = Transaction.objects.all()
  filter_backends = (filters.DjangoFilterBackend,)
  filterset_class = TransactionFilter

  def parse_history_querystring(self):
    try:
      return int(
          self.request.GET.get('history', settings.TRANSACTION_HISTORY_MAX)
      )
    except ValueError:
      return int(settings.TRANSACTION_HISTORY_MAX)

  @swagger_auto_schema(manual_parameters=[custom_transaction_view_parm])
  def list(self, request, *args, **kwargs):
    return super().list(request, *args, **kwargs)

  @openapi_ready
  def get_queryset(self):
    history = self.parse_history_querystring()

    queryset = self.queryset
    return queryset.\
        filter(user=self.request.user).\
        filter(
          datetime__lte=timezone.now(),
          datetime__gt=timezone.now() - datetime.timedelta(days=int(history))
        ).\
        order_by('-datetime')

  @openapi_ready
  def perform_create(self, serializer):
    """Create a new Transaction"""
    serializer.save(user=self.request.user)


class TransactionConsumptionHistoryViewSet(
    CSRFMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
  """Transaction Consumption History API View"""
  serializer_class = TransactionConsumptionHistorySerializer
  queryset = Item.objects.all()
