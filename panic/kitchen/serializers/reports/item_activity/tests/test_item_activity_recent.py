"""Test the RecentActivitySerializer class."""

import json
from datetime import timedelta

import pytz
from django.utils import timezone
from freezegun import freeze_time

from .....models.transaction import Transaction
from .....tests.fixtures.fixtures_django import MockRequest
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..item_activity_last_two_weeks import LastTwoWeeksActivitySerializer
from ..item_activity_recent import RecentActivitySerializer


@freeze_time("2020-01-14")
class TestLastTwoWeeksActivitySerializer(TransactionTestHarness):
  """Test the RecentActivitySerializer class."""

  mute_signals = False

  @classmethod
  def create_data_hook(cls):
    cls.serializer = RecentActivitySerializer
    cls.history_serializer = LastTwoWeeksActivitySerializer
    cls.today = timezone.now()
    cls.two_days_ago = timezone.now() + timedelta(days=-2)
    cls.start_of_month = timezone.now() + timedelta(days=-13)

    cls.positive_transaction = {
        'item': cls.item1,
        'date_object': cls.today - timedelta(days=365),
        'user': cls.user1,
        'quantity': 3
    }

    cls.consumption_today = dict(cls.positive_transaction)
    cls.consumption_today.update({'date_object': cls.today, 'quantity': -3})

    cls.consumption_week_border = dict(cls.positive_transaction)
    cls.consumption_week_border.update({
        'date_object': cls.two_days_ago,
        'quantity': -3
    })

    cls.consumption_month_border = dict(cls.positive_transaction)
    cls.consumption_month_border.update({
        'date_object': cls.start_of_month,
        'quantity': -3
    })

    cls.request = MockRequest(cls.user1)

  def setUp(self):
    self.objects = list()
    self.create_test_instance(**self.positive_transaction)
    self.user1.timezone = pytz.utc.zone
    self.user1.save()

  def _check_timezone(self, deserialized_data):
    self.assertEqual(
        deserialized_data['user_timezone'],
        str(self.user1.timezone),
    )

  def test_deserialize_activity_last_two_weeks_utc(self):
    self.create_test_instance(**self.consumption_today)
    history = Transaction.objects.get_activity_last_two_weeks(self.item1.id)
    deserialized_transaction = self.history_serializer(history, many=True)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self._check_timezone(deserialized)
    self.assertEqual(
        json.dumps(deserialized['activity_last_two_weeks'],),
        json.dumps(deserialized_transaction.data),
    )

  def test_deserialize_activity_last_two_weeks_honolulu(self):
    test_zone = "Pacific/Honolulu"

    self.create_test_instance(**self.consumption_today)
    self.user1.timezone = test_zone
    self.user1.save()
    history = Transaction.objects.get_activity_last_two_weeks(
        self.item1.id,
        zone=test_zone,
    )
    deserialized_transaction = self.history_serializer(history, many=True)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self._check_timezone(deserialized)
    self.assertEqual(
        json.dumps(deserialized['activity_last_two_weeks'],),
        json.dumps(deserialized_transaction.data),
    )

  def test_deserialize_usage_this_week_utc(self):
    self.create_test_instance(**self.consumption_today)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self._check_timezone(deserialized)
    self.assertEqual(
        deserialized['usage_current_week'],
        3,
    )

  def test_deserialize_usage_this_week_honolulu(self):
    zone = "Pacific/Honolulu"
    self.user1.timezone = zone
    self.user1.save()

    self.create_test_instance(**self.consumption_week_border)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self._check_timezone(deserialized)
    self.assertEqual(
        deserialized['usage_current_week'],
        0,
    )

  def test_deserialize_usage_this_month_utc(self):
    self.create_test_instance(**self.consumption_today)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self._check_timezone(deserialized)
    self.assertEqual(
        deserialized['usage_current_month'],
        3,
    )

  def test_deserialize_usage_this_month_honolulu(self):
    zone = "Pacific/Honolulu"
    self.user1.timezone = zone
    self.user1.save()

    self.create_test_instance(**self.consumption_month_border)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self._check_timezone(deserialized)
    self.assertEqual(
        deserialized['usage_current_month'],
        0,
    )
