"""Test the Item Consumption Serializer."""

import json
from datetime import timedelta

import pytz
from django.utils import timezone
from freezegun import freeze_time
from rest_framework.serializers import ErrorDetail, ValidationError

from ....models.transaction import Transaction
from ....tests.fixtures.fixtures_django import MockRequest
from ....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..item_consumption_history import ItemConsumptionHistorySerializer
from ..item_history import ItemHistorySerializer


class TestItemConsumptionHistorySerializer(TransactionTestHarness):
  """Test the Item Consumption Serializer."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer = ItemConsumptionHistorySerializer
    cls.today = timezone.now()
    cls.two_days_ago = timezone.now() + timedelta(days=-2)
    cls.start_of_month = timezone.now() + timedelta(days=-13)

    cls.fields = {"name": 255}

    cls.data = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': -3
    }

    cls.week_border = {
        'item': cls.item1,
        'date_object': cls.two_days_ago,
        'user': cls.user1,
        'quantity': -3
    }

    cls.month_border = {
        'item': cls.item1,
        'date_object': cls.start_of_month,
        'user': cls.user1,
        'quantity': -3
    }

    cls.request = MockRequest(cls.user1)

  def setUp(self):
    self.objects = list()
    self.item1.quantity = 3
    self.item1.save()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  @freeze_time("2020-01-14")
  def test_deserialize_last_two_weeks(self):
    self.create_test_instance(**self.data)
    history = Transaction.objects.get_last_two_weeks(self.item1.id)
    deserialized_transaction = ItemHistorySerializer(history, many=True)

    serialized = self.serializer(
        self.item1,
        data={"timezone": pytz.utc.zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        json.dumps(deserialized['consumption_last_two_weeks']),
        json.dumps(deserialized_transaction.data),
    )

  @freeze_time("2020-01-14")
  def test_deserialize_last_two_weeks_alternate_timezone(self):
    test_zone = "Asia/Hong_Kong"
    self.create_test_instance(**self.data)
    history = Transaction.objects.get_last_two_weeks(
        self.item1.id,
        zone=test_zone,
    )
    deserialized_transaction = ItemHistorySerializer(history, many=True)

    serialized = self.serializer(
        self.item1,
        data={"timezone": test_zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        json.dumps(deserialized['consumption_last_two_weeks']),
        json.dumps(deserialized_transaction.data),
    )

  @freeze_time("2020-01-14")
  def test_deserialize_first_consumption_date(self):
    self.create_test_instance(**self.data)

    serialized = self.serializer(
        self.item1,
        data={"timezone": pytz.utc.zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        deserialized['first_consumption_date'],
        self.today,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_total_consumption(self):
    self.create_test_instance(**self.data)

    serialized = self.serializer(
        self.item1,
        data={"timezone": pytz.utc.zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        deserialized['total_consumption'],
        3,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_consumption_this_week(self):
    self.create_test_instance(**self.data)

    serialized = self.serializer(
        self.item1,
        data={"timezone": pytz.utc.zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        deserialized['consumption_this_week'],
        3,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_consumption_this_week_tz(self):
    zone = "Pacific/Honolulu"
    self.create_test_instance(**self.week_border)

    serialized = self.serializer(
        self.item1,
        data={"timezone": zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        deserialized['consumption_this_week'],
        0,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_consumption_this_month(self):
    self.create_test_instance(**self.data)

    serialized = self.serializer(
        self.item1,
        data={"timezone": pytz.utc.zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        deserialized['consumption_this_month'],
        3,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_consumption_this_month_tz(self):
    zone = "Pacific/Honolulu"
    self.create_test_instance(**self.month_border)

    serialized = self.serializer(
        self.item1,
        data={"timezone": zone},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
    deserialized = serialized.data

    self.assertEqual(
        deserialized['consumption_this_week'],
        0,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_invalid_timezone(self):
    serialized = self.serializer(
        self.item1,
        data={"timezone": "invalid timezone"},
        context={'request': self.request},
    )
    with self.assertRaises(ValidationError) as raised:
      serialized.is_valid(raise_exception=True)

    self.assertEqual(
        raised.exception.detail,
        {
            'timezone': [
                ErrorDetail(
                    string='Please provide a valid timezone string.',
                    code='invalid'
                ),
            ],
        },
    )

  @freeze_time("2020-01-14")
  def test_deserialize_default_timezone(self):
    serialized = self.serializer(
        self.item1,
        data={},
        context={'request': self.request},
    )
    serialized.is_valid(raise_exception=True)
