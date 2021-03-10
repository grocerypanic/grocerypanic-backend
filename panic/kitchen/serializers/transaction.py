"""Serializer for the Transaction model."""

from ..models.transaction import Transaction
from .bases import KitchenBaseModelSerializer


class TransactionSerializer(KitchenBaseModelSerializer):
  """Serializer for Transaction."""

  class Meta:
    model = Transaction
    fields = '__all__'
    read_only_fields = ("id", "date")

  def validate_item(self, item):
    """Ensure item is owned by the current request user.

    :param item: A related item instance for this model.
    :type item: :class:`panic.kitchen.models.item.Item`

    :raises: :class:`rest_framework.serializers.ValidationError`
    """
    self.related_validator(item, "item")
    return item
