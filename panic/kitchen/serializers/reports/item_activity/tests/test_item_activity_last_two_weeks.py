"""Test the RecentActivitySerializer class."""

from datetime import timedelta
from unittest.mock import patch

import pytz
from django.utils import timezone
from freezegun import freeze_time

from .....models.transaction import Transaction
from .....tests.fixtures.fixtures_django import MockRequest, deserialize_date
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from .. import item_activity_last_two_weeks as report_module
from ..item_activity_last_two_weeks import LastTwoWeeksActivitySerializer

REPORT_MODULE = report_module.__name__


@freeze_time("2020-01-14")
class TestItemHistorySerializer(TransactionTestHarness):
  """Test the RecentActivitySerializer class."""

  mute_signals = False

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.serializer = LastTwoWeeksActivitySerializer

    cls.positive_transaction = {
        'item': cls.item1,
        'date_object': cls.today - timedelta(days=365),
        'user': cls.user1,
        'quantity': 3
    }

    cls.consumption_today = dict(cls.positive_transaction)
    cls.consumption_today.update({'date_object': cls.today, 'quantity': -3})

    cls.request = MockRequest(cls.user1)
    cls.test_value = "ExpectedString"

  def setUp(self):
    self.objects = list()
    self.reset_item1()
    self.create_test_instance(**self.positive_transaction)

  def test_deserialize_last_two_weeks_utc(self):
    transaction = self.create_test_instance(**self.consumption_today)
    history = Transaction.objects.get_activity_last_two_weeks(self.item1.id)
    deserialized_transaction = self.serializer(history, many=True)
    deserialized = deserialized_transaction.data

    self.assertEqual(
        deserialize_date(deserialized[0]['date']),
        transaction.datetime.date(),
    )

    self.assertEqual(
        deserialized[0]['change'],
        transaction.quantity,
    )

  def test_deserialize_last_two_weeks_honolulu(self):
    test_zone = "Pacific/Honolulu"
    test_timezone = pytz.timezone(test_zone)

    transaction = self.create_test_instance(**self.consumption_today)
    history = Transaction.objects.get_activity_last_two_weeks(
        self.item1.id,
        zone=test_zone,
    )
    deserialized_transaction = self.serializer(history, many=True)
    deserialized = deserialized_transaction.data

    parsed_date = deserialize_date(deserialized[0]['date'])

    self.assertEqual(
        parsed_date,
        transaction.datetime.astimezone(test_timezone).date(),
    )

    self.assertEqual(
        deserialized[0]['change'],
        transaction.quantity,
    )

  @patch(REPORT_MODULE + ".serializers.Serializer.create")
  def test_create_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = self.serializer(data={})
    return_value = serializer.create(validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)

  @patch(REPORT_MODULE + ".serializers.Serializer.update")
  def test_update_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = self.serializer(data={})
    return_value = serializer.update(instance={}, validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)
