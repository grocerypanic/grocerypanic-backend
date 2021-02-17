"""Test the Inventory Transaction Manager."""

from datetime import timedelta

from freezegun import freeze_time
from rest_framework.serializers import ErrorDetail

from .....exceptions import ProcessingError
from .....tests.fixtures.fixtures_inventory import InventoryTestHarness
from ....inventory import Inventory


@freeze_time("2020-01-14")
class TestAdjustmentManager(InventoryTestHarness):
  """Test the InventoryTransactionManager model manager class."""

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

  @staticmethod
  def __wipe_inventory():
    Inventory.objects.all().delete()

  def __positive_transaction(self):
    transaction = self.create_test_transaction_instance(
        **self.positive_transaction,
    )
    return transaction

  def __double_positive_transaction(self):
    results = []
    for _ in range(0, 2):
      transaction = self.__positive_transaction()
      Inventory.objects.adjust(transaction)
      results.append(transaction)
    return results

  def __check_inventory(self, inventory, **kwargs):
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

  def test_transaction_positive(self):
    transaction = self.__positive_transaction()
    Inventory.objects.adjust(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("transaction__datetime")

    assert len(query) == 1
    self.__check_inventory(
        query[0],
        transaction=transaction,
        remaining=transaction.quantity,
        item=transaction.item,
    )

  def test_transaction_full_debit(self):
    initial_transaction = self.__positive_transaction()
    Inventory.objects.adjust(initial_transaction)

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction,
    )

    Inventory.objects.adjust(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("transaction__datetime")

    assert len(query) == 0

  def test_transaction_double_full_debit(self):
    self.__double_positive_transaction()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_x2,
    )

    Inventory.objects.adjust(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("transaction__datetime")

    assert len(query) == 0

  def test_transaction_partial_debit(self):
    initial_transaction = self.__positive_transaction()
    Inventory.objects.adjust(initial_transaction)

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial,
    )

    Inventory.objects.adjust(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("transaction__datetime")

    assert len(query) == 1
    self.__check_inventory(
        query[0],
        transaction=initial_transaction,
        remaining=(initial_transaction.quantity + transaction.quantity),
        item=initial_transaction.item,
    )

  def test_transaction_double_partial_debit(self):
    initial_transactions = self.__double_positive_transaction()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial_x2,
    )

    Inventory.objects.adjust(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("transaction__datetime")

    assert len(query) == 2
    self.__check_inventory(
        query[0],
        transaction=initial_transactions[0],
        remaining=(initial_transactions[0].quantity + transaction.quantity),
        item=initial_transactions[0].item,
    )

  def test_transaction_double_partial_debit_rollover(self):
    initial_transactions = self.__double_positive_transaction()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial_x2_rollover,
    )

    Inventory.objects.adjust(transaction)

    query = Inventory.objects.\
        filter(item=transaction.item).\
        order_by("transaction__datetime")

    assert len(query) == 1
    self.__check_inventory(
        query[0],
        transaction=initial_transactions[1],
        remaining=1,
        item=initial_transactions[1].item,
    )

  def test_transaction_broken_inventory(self):
    self.item1.quantity = 100
    self.item1.save()

    transaction = self.create_test_transaction_instance(
        **self.negative_transaction_partial_x2_rollover,
    )

    with self.assertRaises(ProcessingError) as raised:
      Inventory.objects.adjust(transaction)

    expected_error_message = (
        f"could not adjust inventory for transaction={transaction.id}, "
        f"item={transaction.item.id}, "
        f"transaction.quantity={transaction.quantity}, "
        f"item.quantity={transaction.item.quantity}"
    )

    self.assertEqual(
        raised.exception.detail,
        ErrorDetail(
            string=expected_error_message, code=ProcessingError.default_code
        )
    )


@freeze_time("2020-01-14")
class TestAdjustmentManagerQueries(InventoryTestHarness):
  """Test the queries used by the AdjustmentManager model manager class."""

  @classmethod
  def create_data_hook(cls):
    cls.purchased_today = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': 3,
    }
    cls.purchased_yesterday = dict(cls.purchased_today)
    cls.purchased_yesterday.update({
        'date_object': cls.today - timedelta(days=1),
    })

  @staticmethod
  def __wipe_inventory():
    Inventory.objects.all().delete()

  def __apply_transaction(self, definition):
    transaction = self.create_test_transaction_instance(**definition,)
    Inventory.objects.adjust(transaction)
    return transaction

  def test_single_record(self):
    self.__apply_transaction(self.purchased_today)

    query = Inventory.objects. \
        filter(item=self.item1). \
        order_by("transaction__datetime")
    expected_results = Inventory.objects.select_inventory_by_item(self.item1)

    self.assertQuerysetEqual(expected_results, map(repr, query))

  def test_two_records(self):
    self.__apply_transaction(self.purchased_today)
    self.__apply_transaction(self.purchased_yesterday)

    query = Inventory.objects.\
        filter(item=self.item1).\
        order_by("transaction__datetime")
    expected_results = Inventory.objects.select_inventory_by_item(self.item1)

    self.assertQuerysetEqual(expected_results, map(repr, query))
