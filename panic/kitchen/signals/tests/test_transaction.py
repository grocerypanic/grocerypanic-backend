"""Test The Transaction model signals."""

from unittest.mock import patch

from django.utils import timezone

from ...tests.fixtures.fixtures_transaction import TransactionTestHarness
from .. import transaction as transaction_module


class TestTransactionPostSaveHandler(TransactionTestHarness):
  """Test the Transaction model's `post_save` signal handler."""

  mute_signals = False

  @classmethod
  def create_data_hook(cls):
    cls.positive_data = {
        'item': cls.item1,
        'date_object': timezone.now(),
        'user': cls.user1,
        'quantity': 3
    }
    cls.negative_data = {
        'item': cls.item1,
        'date_object': timezone.now(),
        'user': cls.user1,
        'quantity': -3
    }

  @patch(transaction_module.__name__ + '.Inventory.objects.adjust')
  def test_create_inventory_from_transaction(self, m_adjust):
    transaction = self.create_test_instance(**self.positive_data)
    m_adjust.assert_called_once_with(transaction)

  @patch(transaction_module.__name__ + '.Inventory.objects.adjust')
  def test_existing_transaction_save_event_noop(self, m_adjust):
    transaction = self.create_test_instance(**self.positive_data)
    transaction.save()

    m_adjust.assert_called_once_with(transaction)
