"""Views for the Transaction model."""

from rest_framework import mixins, viewsets

from ..models.transaction import Transaction
from ..serializers.transaction import TransactionSerializer
from .bases import KitchenBaseView


class BaseTransactionView(
    KitchenBaseView,
):
  """Base Transaction view."""

  queryset = Transaction.objects.all()
  serializer_class = TransactionSerializer


class TransactionViewSet(
    BaseTransactionView,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
  """Transaction API view."""
