"""Test the Transaction Managers and Expiry Calculator."""

from datetime import timedelta
from unittest.mock import Mock, patch

from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time

import kitchen
from ..models.transaction import Transaction
from ..models.transaction_managers import ItemExpirationCalculator
from .fixtures.transaction import TransactionTestHarness


class MockExpiryCalculator:
  mock = Mock()
  mock_reconcile = Mock()
  mock_save = Mock()
  quantity = None
  item = None
  reconcile_transaction_history = None
  write_expiry_to_item_model = None

  @classmethod
  def reset(cls):
    cls.mock.reset_mock()
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

  def create_timebatch(self):
    t_today = self.create_test_instance(**self.transaction1)
    t_yesterday = self.create_test_instance(**self.transaction2)
    t_tomorrow = self.create_test_instance(**self.transaction3)
    return {"today": t_today, "yesterday": t_yesterday, "tomorrow": t_tomorrow}

  def tearDown(self):
    super().tearDown()
    self.item1.expired = 0
    self.item1.quantity = 3
    self.item1.next_to_expire = 0
    self.item1.save()


class TestItemExpirationCalculator(TestHarnessWithTestData):

  def create_batch_with_total(self):
    batch = self.create_timebatch()

    total_quantity = 0
    total_quantity += batch['yesterday'].quantity
    total_quantity += batch['today'].quantity
    total_quantity += batch['tomorrow'].quantity
    return batch, total_quantity

  @freeze_time("2020-01-14")
  def test_reconcile_transaction_history(self):
    self.create_timebatch()

    with patch(
        kitchen.__name__ +
        '.models.transaction_managers.ItemExpirationCalculator'
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
    self.create_timebatch()

    with patch(
        kitchen.__name__ +
        '.models.transaction_managers.ItemExpirationCalculator'
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

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_pos_qty(self):
    batch, total_quantity = self.create_batch_with_total()

    calculator = ItemExpirationCalculator(self.item1)
    result = calculator.reconcile_single_transaction(batch['yesterday'])
    self.assertEqual(result, total_quantity)
    self.assertEqual(calculator.expired, 0)

  @freeze_time("2021-01-14")
  def test_reconcile_single_transaction_pos_qty_future(self):
    batch, total_quantity = self.create_batch_with_total()

    calculator = ItemExpirationCalculator(self.item1)
    result = calculator.reconcile_single_transaction(batch['yesterday'])
    self.assertEqual(result, total_quantity)
    self.assertEqual(calculator.expired, batch['yesterday'].quantity)

  @freeze_time("2020-01-14")
  def test_reconcile_single_transaction_neg_qty(self):
    batch, total_quantity = self.create_batch_with_total()

    batch['yesterday'].quantity = -3
    batch['yesterday'].save()

    calculator = ItemExpirationCalculator(self.item1)
    result = calculator.reconcile_single_transaction(batch['yesterday'])
    self.assertEqual(result, total_quantity)
    self.assertEqual(calculator.expired, -3)

  @freeze_time("2021-01-14")
  def test_reconcile_single_transaction_neg_qty_future(self):
    batch, total_quantity = self.create_batch_with_total()

    batch['yesterday'].quantity = -3
    batch['yesterday'].save()

    calculator = ItemExpirationCalculator(self.item1)
    result = calculator.reconcile_single_transaction(batch['yesterday'])
    self.assertEqual(result, total_quantity)
    self.assertEqual(calculator.expired, -3)


class TestExpiryManager(TestHarnessWithTestData):

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
        kitchen.__name__ +
        '.models.transaction_managers.ItemExpirationCalculator'
    ) as calculator:
      calculator.return_value = MockExpiryCalculator

      with patch(
          kitchen.__name__ +
          '.models.transaction_managers.ExpiryManager.get_item_history'
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
        kitchen.__name__ +
        '.models.transaction_managers.ItemExpirationCalculator'
    ) as calculator:

      calculator.return_value = MockExpiryCalculator
      Transaction.expiration.update(transaction)
      MockExpiryCalculator.mock_reconcile.assert_not_called()
      MockExpiryCalculator.mock_save.assert_called_once()


class TestConsumptionHistoryManagerTwoWeeks(TestHarnessWithTestData):

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    cls.today = timezone.now()
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']

  @freeze_time("2020-01-14")
  def create_lower_bounds_edge_case_transaction(self):
    edge_case = (
        timezone.now() - timedelta(days=settings.TRANSACTION_HISTORY_MAX)
    )
    edge_case_transaction = {
        'item': self.item1,
        'date_object': edge_case,
        'user': self.user1,
        'quantity': 3
    }
    self.create_test_instance(**edge_case_transaction)

  @freeze_time("2020-01-14")
  def create_another_user_transaction(self):
    another_user_transaction = {
        'item': self.item2,
        'date_object': timezone.now(),
        'user': self.user2,
        'quantity': 3
    }
    self.create_test_instance(**another_user_transaction)

  @freeze_time("2020-01-14")
  def test_last_two_weeks(self):
    self.create_timebatch()

    start_of_window = timezone.now()
    end_of_window = start_of_window - timedelta(
        days=int(settings.TRANSACTION_HISTORY_MAX)
    )

    self.create_lower_bounds_edge_case_transaction()
    self.create_another_user_transaction()

    received = Transaction.consumption.get_last_two_weeks(self.item1)
    expected = Transaction.objects.filter(
        item=self.item1,
        datetime__date__lte=start_of_window,
        datetime__date__gte=end_of_window
    ).order_by('-datetime')

    self.assertQuerysetEqual(received, map(repr, expected))

  @freeze_time("2020-01-14")
  def test_last_two_weeks_no_history(self):

    received = Transaction.consumption.get_last_two_weeks(self.item1)
    self.assertQuerysetEqual(received, map(repr, []))


class TestConsumptionHistoryManagerStats(TransactionTestHarness):

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):

    cls.initial_transaction = {
        'item': cls.item1,
        'date_object': timezone.now() + timedelta(days=-90),
        'user': cls.user1,
        'quantity': 3000
    }

    cls.today = timezone.now()
    cls.dates = dict()

    cls.dates['yesterday'] = timezone.now() + timedelta(days=-1)
    cls.dates['two_days_ago'] = timezone.now() + timedelta(days=-2)
    cls.dates['last_week'] = timezone.now() + timedelta(days=-4)
    cls.dates['last_month'] = timezone.now() + timedelta(days=-17)
    cls.dates['last_year'] = timezone.now() + timedelta(days=-27)
    cls.dates['two_months_ago'] = timezone.now() + timedelta(days=-67)

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    cls.today = timezone.now()
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']

  def create_transaction_history(self):
    self.create_test_instance(**self.initial_transaction)
    for value in self.dates.values():
      self.create_test_instance(
          item=self.item1, date_object=value, user=self.user1, quantity=-3
      )

  def setUp(self):
    self.item1.quantity = 0
    self.item1.save()
    super().setUp()

  @freeze_time("2020-01-14")
  def test_get_first_consumption(self):
    self.create_transaction_history()
    first_consumption = Transaction.objects.filter(
        item=self.item1.id,
        quantity__lt=0,
    ).order_by('datetime',).first().datetime

    self.assertEqual(
        first_consumption,
        Transaction.consumption.get_first_consumption(self.item1.id)
    )

  @freeze_time("2020-01-14")
  def test_get_first_consumption_another_user(self):
    self.create_transaction_history()

    self.assertIsNone(
        Transaction.consumption.get_first_consumption(self.item2.id)
    )

  @freeze_time("2020-01-14")
  def test_get_first_consumption_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertIsNone(
        Transaction.consumption.get_first_consumption(self.item1.id)
    )

  @freeze_time("2020-01-14")
  def test_get_total_consumption(self):
    self.create_transaction_history()
    expected = len(self.dates) * 3

    self.assertEqual(
        expected, Transaction.consumption.get_total_consumption(self.item1.id)
    )

  @freeze_time("2020-01-14")
  def test_get_total_consumption_another_user(self):
    self.create_transaction_history()

    self.assertEqual(
        0, Transaction.consumption.get_total_consumption(self.item2.id)
    )

  @freeze_time("2020-01-14")
  def test_get_total_consumption_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertEqual(
        0, Transaction.consumption.get_total_consumption(self.item1.id)
    )
