"""Test the Item History Serializer."""

from unittest.mock import patch

import pytz
from django.utils import timezone
from freezegun import freeze_time

from ....models.transaction import Transaction
from ....tests.fixtures.fixtures_django import MockRequest, deserialize_date
from ....tests.fixtures.fixtures_transaction import TransactionTestHarness
from .. import item_history
from ..item_history import ItemHistorySerializer


class TestItemHistorySerializer(TransactionTestHarness):
  """Test the Item History Serializer."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.fields = {"name": 255}

    cls.data = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': -3
    }
    cls.request = MockRequest(cls.user1)
    cls.test_value = "ExpectedString"

  def setUp(self):
    self.objects = list()
    self.item1.quantity = 3
    self.item1.save()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  @freeze_time("2020-01-14")
  def test_deserialize_last_two_weeks(self):
    transaction = self.create_test_instance(**self.data)
    history = Transaction.objects.get_last_two_weeks(self.item1.id)
    deserialized_transaction = ItemHistorySerializer(history, many=True)
    deserialized = deserialized_transaction.data

    self.assertEqual(
        deserialize_date(deserialized[0]['date']),
        transaction.datetime.date(),
    )

    self.assertEqual(
        deserialized[0]['quantity'],
        transaction.quantity,
    )

  @freeze_time("2020-01-14")
  def test_deserialize_last_two_weeks_alternate_timezone(self):
    test_zone = "Asia/Hong_Kong"

    test_timezone = pytz.timezone(test_zone)
    transaction = self.create_test_instance(**self.data)
    history = Transaction.objects.get_last_two_weeks(
        self.item1.id,
        zone=test_zone,
    )
    deserialized_transaction = ItemHistorySerializer(history, many=True)
    deserialized = deserialized_transaction.data
    parsed_date = deserialize_date(deserialized[0]['date'])

    naive_transaction_datetime = transaction.datetime.replace(tzinfo=None)

    self.assertEqual(
        parsed_date,
        test_timezone.localize(naive_transaction_datetime).date(),
    )

    self.assertEqual(
        deserialized[0]['quantity'],
        transaction.quantity,
    )

  @patch(item_history.__name__ + ".serializers.Serializer.create")
  def test_create_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = ItemHistorySerializer(data={})
    return_value = serializer.create(validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)

  @patch(item_history.__name__ + ".serializers.Serializer.update")
  def test_update_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = ItemHistorySerializer(data={})
    return_value = serializer.update(instance={}, validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)
