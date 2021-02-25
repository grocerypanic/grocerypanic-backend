"""Test the Transaction Consumption Manager."""

import random
from datetime import timedelta

import pytz
from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time

from .....tests.fixtures.fixtures_freezegun import to_realdate
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ....transaction import Transaction


@freeze_time("2020-01-14")
class TestConsumptionHistoryManagerWithoutData(TransactionTestHarness):
  """Test the Consumption History Manager without any item history present."""

  mute_signals = False

  def test_last_two_weeks_no_history(self):

    received = Transaction.objects.get_last_two_weeks(self.item1)
    self.assertQuerysetEqual(received, map(repr, []))

  def test_get_first_consumption_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertIsNone(Transaction.objects.get_first_consumption(self.item1.id))

  def test_get_total_consumption_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertEqual(
        0, Transaction.objects.get_total_consumption(self.item1.id)
    )


@freeze_time("2020-01-14")
class TestConsumptionHistoryManagerTwoWeeks(TransactionTestHarness):
  """Test the CHM 'get_last_two_weeks' method with item history created."""

  mute_signals = False

  user2: object
  item2: object

  @classmethod
  def create_randomized_instance(cls, **kwargs):
    offset = random.randint(0, 9600)
    modified = dict(kwargs)
    modified.update({
        'date_object': kwargs['date_object'] + timedelta(seconds=offset)
    })
    return cls.create_instance(**modified)

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.transaction_quantity = -3.0
    cls.last_week = timezone.now() - timedelta(days=8)
    cls.yesterday = timezone.now() + timedelta(days=-1)
    cls.last_year = timezone.now() + timedelta(days=-365)

    def generate_transaction_data(datetime_object, quantity=None):

      if quantity is None:
        quantity = cls.transaction_quantity

      return {
          'item': cls.item1,
          'date_object': datetime_object,
          'user': cls.user1,
          'quantity': quantity
      }

    cls.transaction_init_item1 = generate_transaction_data(cls.last_year, 200)
    cls.purchase_today = generate_transaction_data(
        cls.today,
        abs(cls.transaction_quantity),
    )
    cls.purchase_yesterday = generate_transaction_data(
        cls.yesterday,
        abs(cls.transaction_quantity),
    )
    cls.purchase_last_week = generate_transaction_data(
        cls.last_week,
        abs(cls.transaction_quantity),
    )

    cls.consumption_today = generate_transaction_data(cls.today)
    cls.consumption_yesterday = generate_transaction_data(cls.yesterday)
    cls.consumption_last_week = generate_transaction_data(cls.last_week)
    cls.consumption_last_year = generate_transaction_data(cls.last_year)

    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']

    cls._create_initial_item_quantities()
    cls._create_lower_bounds_edge_case_transaction()
    cls._create_another_user_transaction()
    cls._create_test_transactions()

  @classmethod
  def _create_initial_item_quantities(cls):
    cls.transaction_init_item2 = dict(cls.transaction_init_item1)
    cls.transaction_init_item2.update({
        'item': cls.item2,
    })

    cls.create_randomized_instance(**cls.transaction_init_item1)
    cls.create_randomized_instance(**cls.transaction_init_item2)

  @classmethod
  def _create_another_user_transaction(cls):
    another_user_transaction = dict(cls.consumption_today)
    another_user_transaction.update({
        'item': cls.item2,
        'user': cls.user2,
    })
    cls.create_randomized_instance(**another_user_transaction)

  @classmethod
  def _create_lower_bounds_edge_case_transaction(cls):
    cls.edge_case = (
        timezone.now() - (
            timedelta(days=settings.TRANSACTION_HISTORY_MAX,) +
            timedelta(hours=1,)
        )
    )
    edge_case_transaction = dict(cls.consumption_today)
    edge_case_transaction.update({
        'date_object': cls.edge_case,
    })
    cls.create_instance(**edge_case_transaction)

  @classmethod
  def _create_test_transactions(cls):
    cls.create_randomized_instance(**cls.consumption_today)
    cls.create_randomized_instance(**cls.consumption_today)
    cls.create_randomized_instance(**cls.consumption_today)
    cls.create_randomized_instance(**cls.purchase_today)
    cls.create_randomized_instance(**cls.consumption_yesterday)
    cls.create_randomized_instance(**cls.consumption_yesterday)
    cls.create_randomized_instance(**cls.consumption_yesterday)
    cls.create_randomized_instance(**cls.purchase_yesterday)
    cls.create_randomized_instance(**cls.consumption_last_week)
    cls.create_randomized_instance(**cls.consumption_last_week)
    cls.create_randomized_instance(**cls.consumption_last_week)
    cls.create_randomized_instance(**cls.purchase_last_week)

  def test_last_two_weeks_utc(self):
    consumption_amount = abs(self.transaction_quantity)
    expected_results = [
        {
            'date': self.today,
            'quantity': 3 * consumption_amount
        },
        {
            'date': self.yesterday,
            'quantity': 3 * consumption_amount
        },
        {
            'date': self.last_week,
            'quantity': 3 * consumption_amount
        },
    ]

    received = Transaction.objects.get_last_two_weeks(self.item1)

    self.assertQuerysetEqual(
        to_realdate(expected_results, 'date'),
        map(repr, received),
    )

  def test_last_two_weeks_honolulu(self):
    test_tz = "Pacific/Honolulu"

    consumption_amount = abs(self.transaction_quantity)
    honolulu_edge_case = self.edge_case + timedelta(days=1)

    expected_results = [
        {
            'date': self.today,
            'quantity': 3 * consumption_amount
        },
        {
            'date': self.yesterday,
            'quantity': 3 * consumption_amount
        },
        {
            'date': self.last_week,
            'quantity': 3 * consumption_amount
        },
        {
            'date': honolulu_edge_case,
            'quantity': consumption_amount
        },
    ]

    received = Transaction.objects.get_last_two_weeks(
        self.item1,
        zone=test_tz,
    )

    self.assertQuerysetEqual(
        to_realdate(expected_results, 'date', offset=1),
        map(repr, received),
    )

  def test_last_two_weeks_tz_diff(self):
    test_tz1 = "Pacific/Honolulu"
    test_tz2 = "Asia/Hong_Kong"

    received1 = Transaction.objects.get_last_two_weeks(
        self.item1,
        zone=test_tz1,
    )

    received2 = Transaction.objects.get_last_two_weeks(
        self.item1,
        zone=test_tz2,
    )

    self.assertEqual(
        len(received1),
        len(received2),
    )

    for index, transaction in enumerate(received1):
      assert received2[index]['date'] != transaction['date']
      assert received2[index]['quantity'] == transaction['quantity']


@freeze_time("2020-01-14")
class TestConsumptionHistoryManagerStats(TransactionTestHarness):
  """Test the CHM 'get_STATISTIC' methods with item history created."""

  initial_transaction: dict
  dates: dict

  mute_signals = False

  @classmethod
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
    cls.dates['start_of_month'] = timezone.now() + timedelta(days=-13)
    cls.dates['last_month'] = timezone.now() + timedelta(days=-17)
    cls.dates['last_year'] = timezone.now() + timedelta(days=-27)
    cls.dates['two_months_ago'] = timezone.now() + timedelta(days=-67)

    cls.__create_transaction_history()

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    cls.today = timezone.now()
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']

  @classmethod
  def __create_transaction_history(cls):
    cls.create_instance(**cls.initial_transaction)
    for value in cls.dates.values():
      cls.create_instance(
          item=cls.item1, date_object=value, user=cls.user1, quantity=-3
      )

  def test_get_first_consumption_utc(self):
    self.assertEqual(
        self.dates['two_months_ago'],
        Transaction.objects.get_first_consumption(self.item1.id)
    )

  def test_get_first_consumption_honolulu(self):
    zone = "Pacific/Honolulu"

    self.assertEqual(
        self.dates['two_months_ago'].astimezone(pytz.timezone(zone)),
        Transaction.objects.get_first_consumption(
            self.item1.id,
            zone=zone,
        )
    )

  def test_get_first_consumption_tz_difference(self):
    zone1 = "UTC"
    zone2 = "Pacific/Honolulu"

    first_consumption_tz1 = Transaction.objects.get_first_consumption(
        self.item1.id,
        zone=zone1,
    )
    first_consumption_tz2 = Transaction.objects.get_first_consumption(
        self.item1.id,
        zone=zone2,
    )

    self.assertEqual(
        first_consumption_tz1,
        first_consumption_tz2,
    )

    self.assertNotEqual(
        first_consumption_tz1.date(),
        first_consumption_tz2.date(),
    )

  def test_get_first_consumption_another_user(self):
    self.assertIsNone(Transaction.objects.get_first_consumption(self.item2.id))

  def test_get_total_consumption(self):
    expected = len(self.dates) * 3

    self.assertEqual(
        expected, Transaction.objects.get_total_consumption(self.item1.id)
    )

  def test_get_total_consumption_another_user(self):
    self.assertEqual(
        0, Transaction.objects.get_total_consumption(self.item2.id)
    )

  def test_get_current_week_consumption_utc(self):
    self.assertEqual(
        6, Transaction.objects.get_current_week_consumption(self.item1.id)
    )

  def test_get_current_week_consumption_honolulu(self):
    zone = "Pacific/Honolulu"

    self.assertEqual(
        3,
        Transaction.objects.get_current_week_consumption(
            self.item1.id,
            zone=zone,
        )
    )

  def test_get_current_week_consumption_tz_difference(self):
    zone1 = "UTC"
    zone2 = "Pacific/Honolulu"

    self.assertNotEqual(
        Transaction.objects.get_current_week_consumption(
            self.item1.id, zone=zone1
        ),
        Transaction.objects.get_current_week_consumption(
            self.item1.id,
            zone=zone2,
        ),
    )

  def test_get_current_week_consumption_another_user(self):
    self.assertEqual(
        0, Transaction.objects.get_current_week_consumption(self.item2.id)
    )

  def test_get_current_month_consumption_utc(self):
    self.assertEqual(
        12, Transaction.objects.get_current_month_consumption(self.item1.id)
    )

  def test_get_current_month_consumption_honolulu(self):
    zone = "Pacific/Honolulu"

    self.assertEqual(
        9,
        Transaction.objects.get_current_month_consumption(
            self.item1.id,
            zone=zone,
        )
    )

  def test_get_current_month_consumption_tz_difference(self):
    zone1 = "UTC"
    zone2 = "Pacific/Honolulu"

    self.assertNotEqual(
        Transaction.objects.get_current_month_consumption(
            self.item1.id, zone=zone1
        ),
        Transaction.objects.get_current_month_consumption(
            self.item1.id,
            zone=zone2,
        ),
    )

  def test_get_current_month_consumption_another_user(self):
    self.assertEqual(
        0, Transaction.objects.get_current_month_consumption(self.item2.id)
    )
