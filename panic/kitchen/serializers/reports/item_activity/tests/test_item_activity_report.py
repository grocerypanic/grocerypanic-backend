"""Test the ItemActivityReportSerializer class."""

import json
from datetime import timedelta

import pytz
from django.utils import timezone
from freezegun import freeze_time

from .....models.managers.transaction import activity as manager_module
from .....tests.fixtures.fixtures_django import MockRequest
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from .. import ItemActivityReportSerializer
from ..item_activity_recent import RecentActivitySerializer

MANAGER_MODULE = manager_module.__name__


@freeze_time("2020-01-14")
class TestItemActivitySerializer(TransactionTestHarness):
  """Test the ItemActivityReportSerializer class."""

  mute_signals = False

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemActivityReportSerializer
    cls.today = timezone.now()
    cls.one_year_ago = cls.today - timedelta(days=365)

    cls.positive_transaction = {
        'item': cls.item1,
        'date_object': cls.one_year_ago,
        'user': cls.user1,
        'quantity': 3
    }

    cls.consumption_today = dict(cls.positive_transaction)
    cls.consumption_today.update({'date_object': cls.today, 'quantity': -3})

    cls.request = MockRequest(cls.user1)

    cls.create_instance(**cls.positive_transaction)
    cls.create_instance(**cls.consumption_today)

  def setUp(self):
    self.objects = list()
    self.user1.timezone = pytz.utc.zone
    self.user1.save()

  def test_deserialize_activity_first(self):
    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )

    deserialized = serialized.data

    self.assertEqual(
        deserialized['activity_first'],
        self.item1.activity_first,
    )

  def test_deserialize_usage_total(self):
    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )

    deserialized = serialized.data

    self.assertEqual(
        deserialized['usage_total'],
        self.item1.usage_total,
    )

  def test_usage_avg_week(self):

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self.assertEqual(
        deserialized['usage_avg_week'],
        self.item1.usage_avg_week,
    )

  def test_usage_avg_month(self):
    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self.assertEqual(
        deserialized['usage_avg_month'],
        self.item1.usage_avg_month,
    )

  def test_deserialize_recent_activity(self):
    deserialized_transaction = RecentActivitySerializer(self.item1)

    serialized = self.serializer(
        self.item1,
        context={'request': self.request},
    )
    deserialized = serialized.data

    self.assertEqual(
        json.dumps(deserialized['recent_activity'],),
        json.dumps(deserialized_transaction.data),
    )
