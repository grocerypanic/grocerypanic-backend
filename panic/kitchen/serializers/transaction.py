"""Serializer for the Transaction Model"""

from ..models.transaction import Transaction
from .bases import RelatedValidatorModelSerializer


class TransactionSerializer(RelatedValidatorModelSerializer):
  """Serializer for Transactions"""

  class Meta:
    model = Transaction
    fields = '__all__'
    read_only_fields = ("id", "date")

  def validate_item(self, item):
    self.related_validator(item, "item")
    return item
