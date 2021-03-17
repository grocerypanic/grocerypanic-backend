"""Test the Transaction Activity model manager."""

from collections import OrderedDict
from datetime import timedelta

import pendulum
import pytz
from django.conf import settings
from django.utils import timezone
from freezegun import freeze_time

from .....tests.fixtures.fixtures_freezegun import to_realdate
from ....transaction import Transaction
from .fixtures.fixtures_activity import ActivityManagerTestHarness


@freeze_time("2020-01-14")
class TestActivityManagerWithoutData(ActivityManagerTestHarness):
  """Test the ActivityManager model manager without item history."""

  mute_signals = False
  randomize_datetimes = False

  def test_activity_last_two_weeks_no_history(self):
    expected_results = []
    for day in range(0, 14):
      expected_results.append({
          'date': timezone.now() - timedelta(days=day),
          'change': 0,
      })
    expected_results = to_realdate(expected_results, 'date')
    received = Transaction.objects.get_activity_last_two_weeks(self.item1)
    self.assertListEqual(received, expected_results)

  def test_get_activity_first_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertIsNone(Transaction.objects.get_activity_first(self.item1.id))

  def test_get_usage_total_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertEqual(0, Transaction.objects.get_usage_total(self.item1.id))

  def test_get_usage_current_week_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertEqual(
        0, Transaction.objects.get_usage_current_week(self.item1.id)
    )

  def test_get_usage_current_month_no_history(self):
    assert Transaction.objects.all().count() == 0

    self.assertEqual(
        0, Transaction.objects.get_usage_current_month(self.item1.id)
    )


@freeze_time("2020-01-14")
class TestActivityManagerTwoWeeks(ActivityManagerTestHarness):
  """Test the AM 'get_last_two_weeks' method with item history created."""

  mute_signals = False
  randomize_datetimes = True

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.transaction_quantity = 3.0

    cls.initial_transaction1 = {
        'item': cls.item1,
        'date_object': timezone.now() + timedelta(days=-700),
        'user': cls.user1,
        'quantity': 3000
    }

    cls.dates = OrderedDict()
    cls.dates['last_year'] = cls.today + timedelta(days=-365)
    cls.dates['last_week'] = cls.today + timedelta(days=-8)
    cls.dates['yesterday'] = cls.today + timedelta(days=-1)
    cls.dates['today'] = cls.today

    purchase = cls.transaction_quantity
    consumption = -1 * cls.transaction_quantity
    create_pattern = [purchase, consumption, consumption, consumption]

    cls.create_transaction_history(create_pattern)
    cls._create_another_user_transaction()
    cls._create_lower_bounds_edge_case_transaction(
        settings.TRANSACTION_HISTORY_MAX - 1
    )

  def test_activity_last_two_weeks_utc(self):
    consumption_amount = abs(self.transaction_quantity)
    expected_results = [
        {
            'date': self.dates['today'],
            'change': -2 * consumption_amount
        },
        {
            'date': self.dates['yesterday'],
            'change': -2 * consumption_amount
        },
        {
            'date': self.dates['today'] - timedelta(days=2),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=3),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=4),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=5),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=6),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=7),
            'change': 0
        },
        {
            'date': self.dates['last_week'],
            'change': -2 * consumption_amount
        },
        {
            'date': self.dates['today'] - timedelta(days=9),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=10),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=11),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=12),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=13),
            'change': 0
        },
    ]

    received = Transaction.objects.get_activity_last_two_weeks(self.item1)

    self.assertListEqual(
        to_realdate(expected_results, 'date'),
        received,
    )

  def test_activity_last_two_weeks_honolulu(self):
    test_tz = "Pacific/Honolulu"

    consumption_amount = abs(self.transaction_quantity)
    honolulu_edge_case = self.dates['edge_case'] + timedelta(days=1)

    expected_results = [
        {
            'date': self.dates['today'],
            'change': -2 * consumption_amount
        },
        {
            'date': self.dates['yesterday'],
            'change': -2 * consumption_amount
        },
        {
            'date': self.dates['today'] - timedelta(days=2),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=3),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=4),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=5),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=6),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=7),
            'change': 0
        },
        {
            'date': self.dates['last_week'],
            'change': -2 * consumption_amount
        },
        {
            'date': self.dates['today'] - timedelta(days=9),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=10),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=11),
            'change': 0
        },
        {
            'date': self.dates['today'] - timedelta(days=12),
            'change': 0
        },
        {
            'date': honolulu_edge_case,
            'change': -2 * consumption_amount
        },
    ]
    expected_results = to_realdate(expected_results, 'date', offset=1)

    received = Transaction.objects.get_activity_last_two_weeks(
        self.item1,
        zone=test_tz,
    )

    self.assertListEqual(
        expected_results,
        received,
    )

  def test_activity_last_two_weeks_tz_diff(self):
    test_tz1 = "Pacific/Honolulu"
    test_tz2 = "Asia/Hong_Kong"

    received1 = Transaction.objects.get_activity_last_two_weeks(
        self.item1,
        zone=test_tz1,
    )

    received2 = Transaction.objects.get_activity_last_two_weeks(
        self.item1,
        zone=test_tz2,
    )

    self.assertEqual(
        len(received1),
        len(received2),
    )

    for index, transaction in enumerate(received1):
      assert received2[index]['date'] != transaction['date']
      assert received2[index]['change'] == transaction['change']


@freeze_time("2020-01-14")
class TestActivityManagerStats(ActivityManagerTestHarness):
  """Test the AM 'get_STATISTIC' methods with item history created."""

  mute_signals = False
  randomize_datetimes = False
  user2_initial_transaction = False

  @classmethod
  def create_data_hook(cls):

    cls.first_activity = timezone.now() + timedelta(days=-90)

    cls.initial_transaction1 = {
        'item': cls.item1,
        'date_object': cls.first_activity,
        'user': cls.user1,
        'quantity': 3000
    }

    cls.transaction_quantity = -3.0

    cls.now = pendulum.now('UTC')
    cls.dates = OrderedDict()

    cls.dates['two_months_ago'] = cls.now + timedelta(days=-67)
    cls.dates['last_year'] = cls.now + timedelta(days=-27)
    cls.dates['last_month'] = cls.now + timedelta(days=-17)
    cls.dates['start_of_month'] = cls.now + timedelta(days=-13)
    cls.dates['last_week'] = cls.now + timedelta(days=-4)
    cls.dates['two_days_ago'] = cls.now + timedelta(days=-2)
    cls.dates['yesterday'] = cls.now + timedelta(days=-1)

    purchase = cls.transaction_quantity
    consumption = -1 * cls.transaction_quantity
    create_pattern = [purchase, consumption]

    cls.create_transaction_history(create_pattern)

  def test_get_activity_first_utc(self):
    self.assertEqual(
        self.first_activity,
        Transaction.objects.get_activity_first(self.item1.id)
    )

  def test_get_activity_first_honolulu(self):
    zone = "Pacific/Honolulu"

    self.assertEqual(
        self.first_activity.astimezone(pytz.timezone(zone)),
        Transaction.objects.get_activity_first(
            self.item1.id,
            zone=zone,
        )
    )

  def test_get_activity_first_tz_difference(self):
    zone1 = "UTC"
    zone2 = "Pacific/Honolulu"

    first_consumption_tz1 = Transaction.objects.get_activity_first(
        self.item1.id,
        zone=zone1,
    )
    first_consumption_tz2 = Transaction.objects.get_activity_first(
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

  def test_get_activity_first_another_user(self):
    self.assertIsNone(Transaction.objects.get_activity_first(self.item2.id))

  def test_get_usage_total(self):
    expected = len(self.dates) * 3

    self.assertEqual(
        expected, Transaction.objects.get_usage_total(self.item1.id)
    )

  def test_get_usage_total_another_user(self):
    self.assertEqual(0, Transaction.objects.get_usage_total(self.item2.id))

  def test_get_usage_current_week_utc(self):
    self.assertEqual(
        6, Transaction.objects.get_usage_current_week(self.item1.id)
    )

  def test_get_usage_current_week_honolulu(self):
    zone = "Pacific/Honolulu"

    self.assertEqual(
        3, Transaction.objects.get_usage_current_week(
            self.item1.id,
            zone=zone,
        )
    )

  def test_get_usage_current_week_tz_difference(self):
    zone1 = "UTC"
    zone2 = "Pacific/Honolulu"

    self.assertNotEqual(
        Transaction.objects.get_usage_current_week(self.item1.id, zone=zone1),
        Transaction.objects.get_usage_current_week(
            self.item1.id,
            zone=zone2,
        ),
    )

  def test_get_usage_current_week_another_user(self):
    self.assertEqual(
        0, Transaction.objects.get_usage_current_week(self.item2.id)
    )

  def test_get_usage_current_month_utc(self):
    self.assertEqual(
        12, Transaction.objects.get_usage_current_month(self.item1.id)
    )

  def test_get_usage_current_month_honolulu(self):
    zone = "Pacific/Honolulu"

    self.assertEqual(
        9, Transaction.objects.get_usage_current_month(
            self.item1.id,
            zone=zone,
        )
    )

  def test_get_usage_current_month_tz_difference(self):
    zone1 = "UTC"
    zone2 = "Pacific/Honolulu"

    self.assertNotEqual(
        Transaction.objects.get_usage_current_month(self.item1.id, zone=zone1),
        Transaction.objects.get_usage_current_month(
            self.item1.id,
            zone=zone2,
        ),
    )

  def test_get_usage_current_month_another_user(self):
    self.assertEqual(
        0, Transaction.objects.get_usage_current_month(self.item2.id)
    )
