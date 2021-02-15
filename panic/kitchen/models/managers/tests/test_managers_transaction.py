"""Test the Transaction managers and expiry calculator."""

from datetime import timedelta
from unittest.mock import Mock, patch

from django.utils import timezone
from freezegun import freeze_time

from ....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ...transaction import Transaction
from .. import transaction as transaction_manager
from ..transaction import ItemExpirationCalculator


class MockExpiryCalculator:
  """A mock that functions like the ExpiryCalculator for testing."""

  mock_reconcile = Mock()
  mock_save = Mock()
  quantity = None
  item = None
  reconcile_transaction_history = None
  write_expiry_to_item_model = None

  @classmethod
  def reset(cls):
    cls.mock_reconcile.reset_mock()
    cls.mock_save.reset_mock()

  @classmethod
  def configure(cls, item, quantity):
    cls.reset()

    cls.quantity = quantity
    cls.item = item
    cls.reconcile_transaction_history = cls.mock_reconcile
    cls.write_expiry_to_item_model = cls.mock_save


class TestHarnessWithTestData(TransactionTestHarness):
  """Extend the Transaction test harness by adding data."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.tomorrow = timezone.now() + timedelta(days=1)
    cls.yesterday = timezone.now() + timedelta(days=-1)
    cls.last_year = timezone.now() + timedelta(days=-365)

    cls.transaction1 = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': 3
    }
    cls.transaction2 = {
        'item': cls.item1,
        'date_object': cls.yesterday,
        'user': cls.user1,
        'quantity': 3
    }
    cls.transaction3 = {
        'item': cls.item1,
        'date_object': cls.tomorrow,
        'user': cls.user1,
        'quantity': 3
    }
    cls.transaction4 = {
        'item': cls.item1,
        'date_object': cls.last_year,
        'user': cls.user1,
        'quantity': 3
    }

  @classmethod
  def create_timebatch(cls):
    t_today = cls.create_instance(**cls.transaction1)
    t_yesterday = cls.create_instance(**cls.transaction2)
    t_tomorrow = cls.create_instance(**cls.transaction3)
    return {"today": t_today, "yesterday": t_yesterday, "tomorrow": t_tomorrow}

  def tearDown(self):
    super().tearDown()
    self.item1.expired = 0
    self.item1.quantity = 3
    self.item1.next_to_expire = 0
    self.item1.save()


class TestIECAggregateMethods(TestHarnessWithTestData):
  """Test the high level methods of the IEC (Item Expiry Calculator) class."""

  @freeze_time("2020-01-14")
  def test_reconcile_transaction_history(self):

    with patch(
        transaction_manager.__name__ + '.ItemExpirationCalculator'
        '.reconcile_single_transaction'
    ) as reconciler:

      reconciler.side_effect = [3, 2, 0]
      calculator = ItemExpirationCalculator(self.item1)
      calculator.oldest = self.last_year
      history = [1, 2, 3]
      calculator.reconcile_transaction_history(history)

      reconciler.assert_any_call(history[0])
      reconciler.assert_any_call(history[1])
      reconciler.assert_any_call(history[2])
      assert reconciler.call_count == 3
      assert calculator.quantity == 2
      assert calculator.oldest == timezone.now()

  @freeze_time("2020-01-14")
  def test_reconcile_transaction_history_with_expired(self):
    with patch(
        transaction_manager.__name__ + '.ItemExpirationCalculator'
        '.reconcile_single_transaction'
    ) as reconciler:

      reconciler.side_effect = [3, 2, 0]
      calculator = ItemExpirationCalculator(self.item1)
      calculator.next_to_expire = 1
      calculator.oldest = self.last_year
      history = [1, 2, 3]
      calculator.reconcile_transaction_history(history)

      reconciler.assert_any_call(history[0])
      reconciler.assert_any_call(history[1])
      reconciler.assert_any_call(history[2])
      assert reconciler.call_count == 3
      assert calculator.quantity == 2
      assert calculator.oldest == self.last_year

  def test_write_expiry_to_item_model_expired_items(self):
    next_to_expire = 1
    oldest = self.last_year
    expired = 5

    calculator = ItemExpirationCalculator(self.item1)
    calculator.next_to_expire = next_to_expire
    calculator.oldest = oldest
    calculator.expired = expired

    calculator.write_expiry_to_item_model()

    assert self.item1.next_expiry_quantity == next_to_expire
    assert self.item1.next_expiry_date == (
        self.last_year + timedelta(days=self.item1.shelf_life)
    )
    assert self.item1.expired == expired

  def test_write_expiry_to_item_model_neg_expired_items(self):
    next_to_expire = 1
    oldest = self.last_year
    expired = -5

    calculator = ItemExpirationCalculator(self.item1)
    calculator.next_to_expire = next_to_expire
    calculator.oldest = oldest
    calculator.expired = expired

    calculator.write_expiry_to_item_model()

    assert self.item1.next_expiry_quantity == next_to_expire
    assert self.item1.next_expiry_date == (
        self.last_year + timedelta(days=self.item1.shelf_life)
    )
    assert self.item1.expired == 0


class TestIECTransactions(TestHarnessWithTestData):
  """Test the lower level methods of the IEC (Item Expiry Calculator) class."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    super().create_data_hook()

    cls.positive_past = {
        'item': cls.item1,
        'date_object': cls.yesterday,
        'user': cls.user1,
        'quantity': 3
    }
    cls.positive_future = {
        'item': cls.item1,
        'date_object': cls.tomorrow,
        'user': cls.user1,
        'quantity': 3
    }

    cls.negative_past = {
        'item': cls.item1,
        'date_object': cls.yesterday,
        'user': cls.user1,
        'quantity': -3
    }
    cls.negative_future = {
        'item': cls.item1,
        'date_object': cls.tomorrow,
        'user': cls.user1,
        'quantity': -3
    }

    cls.expired = {
        'item': cls.item1,
        'date_object': cls.last_year,
        'user': cls.user1,
        'quantity': 3
    }

  def create_timebatch(self):
    t_today = self.create_test_instance(**self.transaction1)
    t_yesterday = self.create_test_instance(**self.transaction2)
    t_tomorrow = self.create_test_instance(**self.transaction3)
    return {"today": t_today, "yesterday": t_yesterday, "tomorrow": t_tomorrow}

  def create_batch_with_total(self):
    self.reset_item1()
    batch = self.create_timebatch()

    total_quantity = 0
    total_quantity += batch['yesterday'].quantity
    total_quantity += batch['today'].quantity
    total_quantity += batch['tomorrow'].quantity
    return batch, total_quantity

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_pos_qty(self):
    _, total_quantity = self.create_batch_with_total()

    transaction = self.create_test_instance(**self.positive_past)

    calculator = ItemExpirationCalculator(self.item1)
    remaining = calculator.reconcile_single_transaction(transaction)
    self.assertEqual(remaining, total_quantity)
    self.assertEqual(calculator.expired, 0)

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_pos_qty_future(self):
    _, total_quantity = self.create_batch_with_total()

    transaction = self.create_test_instance(**self.positive_future)

    calculator = ItemExpirationCalculator(self.item1)
    remaining = calculator.reconcile_single_transaction(transaction)
    self.assertEqual(remaining, total_quantity)
    self.assertEqual(calculator.expired, 0)

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_neg_qty(self):
    _, total_quantity = self.create_batch_with_total()

    transaction = self.create_test_instance(**self.negative_past)

    calculator = ItemExpirationCalculator(self.item1)
    remaining = calculator.reconcile_single_transaction(transaction)
    self.assertEqual(remaining, total_quantity + transaction.quantity)

    self.assertEqual(calculator.expired, -3)

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_neg_qty_future(self):
    _, total_quantity = self.create_batch_with_total()

    transaction = self.create_test_instance(**self.negative_future)

    calculator = ItemExpirationCalculator(self.item1)
    remaining = calculator.reconcile_single_transaction(transaction)
    self.assertEqual(remaining, total_quantity + transaction.quantity)

    self.assertEqual(calculator.expired, -3)

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_expired(self):
    _, total_quantity = self.create_batch_with_total()

    transaction = self.create_test_instance(**self.expired)

    calculator = ItemExpirationCalculator(self.item1)
    remaining = calculator.reconcile_single_transaction(transaction)
    self.assertEqual(remaining, total_quantity)
    self.assertEqual(calculator.expired, 3)


class TestExpiryManager(TestHarnessWithTestData):
  """Test the Transaction model's ExpiryManager class."""

  def test_get_item_history_is_correct_order(self):
    batch = self.create_timebatch()
    query_set = Transaction.expiration.get_item_history(self.item1)
    self.assertEqual(batch['yesterday'].id, query_set[2].id)
    self.assertEqual(batch['today'].id, query_set[1].id)
    self.assertEqual(batch['tomorrow'].id, query_set[0].id)

  def test_get_item_history_is_correct_type(self):
    self.create_test_instance(**self.transaction1)
    query_set = Transaction.expiration.get_item_history(self.item1)
    assert len(query_set) == 1
    self.assertIsInstance(query_set[0], Transaction)

  def test_update_with_non_zero_quantity(self):
    transaction = self.create_test_instance(**self.transaction1)
    MockExpiryCalculator.configure(self.item1, 3)
    mock_query_set = [1, 2, 3]

    with patch(
        transaction_manager.__name__ + '.ItemExpirationCalculator'
    ) as calculator:
      calculator.return_value = MockExpiryCalculator

      with patch(
          transaction_manager.__name__ + '.ExpiryManager.get_item_history'
      ) as mock_get_item_history:

        mock_get_item_history.return_value = mock_query_set
        Transaction.expiration.update(transaction)
        MockExpiryCalculator.mock_reconcile.assert_called_once_with(
            mock_query_set
        )
        MockExpiryCalculator.mock_save.assert_called_once()

  def test_update_with_zero_quantity(self):
    transaction = self.create_test_instance(**self.transaction1)

    MockExpiryCalculator.configure(self.item1, 0)

    with patch(
        transaction_manager.__name__ + '.ItemExpirationCalculator'
    ) as calculator:

      calculator.return_value = MockExpiryCalculator
      Transaction.expiration.update(transaction)
      MockExpiryCalculator.mock_reconcile.assert_not_called()
      MockExpiryCalculator.mock_save.assert_called_once()
