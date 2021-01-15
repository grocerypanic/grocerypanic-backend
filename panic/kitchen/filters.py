"""Filters for the Kitchen Application Views."""

from django_filters import CharFilter
from django_filters import rest_framework as simple_filters

from .models.item import Item
from .models.transaction import Transaction


class TransactionFilter(simple_filters.FilterSet):
  item = CharFilter(required=True, field_name='item')

  class Meta:
    model = Transaction
    fields = ['item']


class ItemFilter(simple_filters.FilterSet):

  class Meta:
    model = Item
    fields = ['shelf', 'preferred_stores']
