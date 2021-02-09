"""Test the Inventory Transaction Manager."""

from rest_framework.serializers import ErrorDetail

from .....exceptions import ProcessingError
from .....tests.fixtures.inventory import InventoryTestHarness
from ....inventory import Inventory


class TestTransactionReconcilerManager(InventoryTestHarness):

  @classmethod
  def create_data_hook(cls):
    cls.positive_transaction = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': 3,
    }
    cls.negative_transaction = dict(cls.positive_transaction)
    cls.negative_transaction.update({
        'quantity': -3,
    })
    cls.negative_transaction_x2 = dict(cls.negative_transaction)
    cls.negative_transaction_x2.update({
        'quantity': cls.negative_transaction['quantity'] * 2,
    })
    cls.negative_transaction_partial = dict(cls.positive_transaction)
    cls.negative_transaction_partial.update({
        'quantity': -1,
    })
    cls.negative_transaction_partial_x2 = dict(cls.positive_transaction)
    cls.negative_transaction_partial_x2.update({
        'quantity': cls.negative_transaction_partial['quantity'] * 2,
    })
    cls.negative_transaction_partial_x2_rollover = dict(
        cls.positive_transaction
    )
    cls.negative_transaction_partial_x2_rollover.update({
        'quantity': -1 * ((cls.positive_transaction['quantity'] * 2) - 1),
    })

  def wipe_inventory(self):
    Inventory.objects.all().delete()

  def process_positive_transaction(self):
    transaction = self.create_test_transaction_instance(
        **self.positive_transaction,
    )
    return transaction

  def process_double_positive_transaction(self):
    results = []
    for _ in range(0, 2):
      transaction = self.process_positive_transaction()
      Inventory.objects.process(transaction)
      results.append(transaction)
    return results

  def check_inventory(self, inventory, **kwargs):
    self.assertEqual(
        kwargs['transaction'],
        inventory.transaction,
    )
    self.assertEqual(
        kwargs['remaining'],
        inventory.remaining,
    )
    self.assertEqual(
        kwargs['item'],
        inventory.item,
    )

  def testProcessTransactionPositive(self):
    transaction = self.process_positive_transaction()
    Inventory.objects.process(transaction)

    query = Inventory.objects.filter(item=transaction.item)

    assert len(query) == 1
    self.check_inventory(
        query[0],
        transaction=transaction,
        remaining=transaction.quantity,
        item=transaction.item,
    )

  def testProcessTransactionFullDebit(self):
    initial_transaction = self.process_positive_transaction()
    Inventory.objects.process(initial_transaction)

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction,
    )

    Inventory.objects.process(transaction)

    query = Inventory.objects.filter(item=transaction.item)

    assert len(query) == 0

  def testProcessTransactionDoubleFullDebit(self):
    self.process_double_positive_transaction()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_x2,
    )

    Inventory.objects.process(transaction)

    query = Inventory.objects.filter(item=transaction.item)

    assert len(query) == 0

  def testProcessTransactionPartialDebit(self):
    initial_transaction = self.process_positive_transaction()
    Inventory.objects.process(initial_transaction)

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial,
    )

    Inventory.objects.process(transaction)

    query = Inventory.objects.filter(item=transaction.item)

    assert len(query) == 1
    self.check_inventory(
        query[0],
        transaction=initial_transaction,
        remaining=(initial_transaction.quantity + transaction.quantity),
        item=initial_transaction.item,
    )

  def testProcessTransactionDoublePartialDebit(self):
    initial_transactions = self.process_double_positive_transaction()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial_x2,
    )

    Inventory.objects.process(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("-transaction__datetime")

    assert len(query) == 2
    self.check_inventory(
        query[0],
        transaction=initial_transactions[0],
        remaining=(initial_transactions[0].quantity + transaction.quantity),
        item=initial_transactions[0].item,
    )

  def testProcessTransactionDoublePartialDebitRollover(self):
    initial_transactions = self.process_double_positive_transaction()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial_x2_rollover,
    )

    Inventory.objects.process(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("-transaction__datetime")

    assert len(query) == 1
    self.check_inventory(
        query[0],
        transaction=initial_transactions[1],
        remaining=1,
        item=initial_transactions[1].item,
    )

  def testProcessTransactionBrokenInventory(self):
    self.item1.quantity = 100
    self.item1.save()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial_x2_rollover,
    )

    with self.assertRaises(ProcessingError) as raised:
      Inventory.objects.process(transaction)

    self.assertEqual(
        raised.exception.detail,
        ErrorDetail(
            string=(
                f"Could not process transaction.id={transaction.id} to modify"
                f" item.id={transaction.item.id} quantity",
            ),
            code=ProcessingError.default_code
        )
    )
