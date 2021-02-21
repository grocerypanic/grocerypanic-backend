"""Test the Item Consumption Report Serializer."""

import json
from datetime import timedelta

import pytz
from django.utils import timezone
from freezegun import freeze_time

from ....tests.fixtures.fixtures_django import MockRequest
from ....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..item_consumption_report import ItemConsumptionHistoryReportSerializer
from ..item_recent_consumption import RecentConsumptionSerializer


@freeze_time("2020-01-14")
class TestItemConsumptionHistorySerializer(TransactionTestHarness):
  """Test the UserConsumptionReport serializer."""

  mute_signals = False

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemConsumptionHistoryReportSerializer
    cls.today = timezone.now()
    cls.two_days_ago = timezone.now() + timedelta(days=-2)
    cls.start_of_month = timezone.now() + timedelta(days=-13)

    cls.fields = {"name": 255}

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

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def test_deserialize_first_consumption(self):
    self.create_test_instance(**self.consumption_today)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self.assertEqual(
        deserialized['first_consumption'],
        self.today,
    )

  def test_deserialize_total_consumption(self):
    self.create_test_instance(**self.consumption_today)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self.assertEqual(
        deserialized['total_consumption'],
        3,
    )

  def test_recent_consumption(self):
    self.create_test_instance(**self.consumption_today)
    deserialized_transaction = RecentConsumptionSerializer(self.item1)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self.assertEqual(
        json.dumps(deserialized['recent_consumption'],),
        json.dumps(deserialized_transaction.data),
    )
