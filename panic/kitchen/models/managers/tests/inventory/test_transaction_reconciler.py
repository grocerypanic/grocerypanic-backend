"""Test the Inventory Transaction Manager."""

from .....tests.fixtures.inventory import InventoryTestHarness
from ....inventory import Inventory


class TestTransactionReconcilerManager(InventoryTestHarness):

  @classmethod
  def create_data_hook(cls):
    cls.positive_transaction = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': 3
    }

  def wipe_inventory(self):
    Inventory.objects.all().delete()

  def testProcessTransaction(self):
    transaction = self.create_test_transaction_instance(
        **self.positive_transaction,
    )
    self.wipe_inventory()

    Inventory.objects.process(transaction)

    query = Inventory.objects.filter(transaction=transaction.id)

    assert len(query) == 1
