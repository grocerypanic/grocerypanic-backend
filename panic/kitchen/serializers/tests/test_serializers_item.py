"""Test the Item Serializer."""

import json
from datetime import timedelta

import pytz
from django.utils import timezone
from freezegun import freeze_time
from rest_framework.serializers import ErrorDetail, ValidationError

from ...models.item import Item
from ...models.transaction import Transaction
from ...tests.fixtures.django import MockRequest, deserialize_date
from ...tests.fixtures.item import ItemTestHarness
from ...tests.fixtures.transaction import TransactionTestHarness
from .. import DUPLICATE_OBJECT_MESSAGE
from ..item import (
    ItemConsumptionHistorySerializer,
    ItemHistorySerializer,
    ItemSerializer,
)


class TestItem(ItemTestHarness):

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)

    cls.data = {
        'name': "Canned Beans",
        'shelf_life': 99,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data = {
        'name': "Canned Beans",
        'shelf_life': 109,
        'shelf': cls.shelf1.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
        'quantity': 3
    }

  @staticmethod
  def generate_overload(fields):
    return_list = []
    for key, value in fields.items():
      overloaded = dict()
      overloaded[key] = "abc" * value
      return_list.append(overloaded)
    return return_list

  def testDeserialize(self):
    item = self.create_test_instance(**self.data)
    serialized = self.serializer(item)
    deserialized = serialized.data

    price = '2.00'

    self.assertEqual(deserialized['name'], self.data['name'])
    self.assertEqual(deserialized['shelf_life'], self.data['shelf_life'])
    self.assertEqual(deserialized['shelf'], self.shelf1.id)
    self.assertEqual(deserialized['price'], price)
    self.assertEqual(deserialized['quantity'], self.data['quantity'])
    preferred_stores = [store.id for store in item.preferred_stores.all()]
    self.assertListEqual(deserialized['preferred_stores'], preferred_stores)
    assert 'user' not in deserialized

  def testSerialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Item.objects.filter(name=self.serializer_data['name'])

    assert len(query) == 1
    item = query[0]

    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.shelf_life, self.serializer_data['shelf_life'])
    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.shelf.id, self.shelf1.id)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, self.serializer_data['quantity'])

  def testUniqueConstraint(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    serialized2 = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    with self.assertRaises(ValidationError):
      serialized2.is_valid(raise_exception=True)

    self.assertEqual(
        str(serialized2.errors['non_field_errors'][0]), DUPLICATE_OBJECT_MESSAGE
    )

  def testFieldLengths(self):
    overloads = self.generate_overload(self.fields)
    for overload in overloads:
      local_data = dict(self.data)
      local_data.update(overload)
      with self.assertRaises(ValidationError):
        serialized = self.serializer(
            context={'request': self.request},
            data=local_data,
        )
        serialized.is_valid(raise_exception=True)


class TestItemConsumptionHistorySerializer(TransactionTestHarness):

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
    history = Transaction.consumption.get_last_two_weeks(self.item1.id)
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
    history = Transaction.consumption.get_last_two_weeks(
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
    with self.assertRaises(ValidationError) as err:
      serialized.is_valid(raise_exception=True)

    self.assertEqual(
        err.exception.detail,
        {
            'timezone': {
                'timezone':
                    ErrorDetail(
                        string='Please provide a valid timezone string.',
                        code='invalid'
                    ),
            }
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


class TestItemHistorySerializer(TransactionTestHarness):

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer = ItemConsumptionHistorySerializer
    cls.today = timezone.now()
    cls.fields = {"name": 255}

    cls.data = {
        'item': cls.item1,
        'date_object': cls.today,
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
    transaction = self.create_test_instance(**self.data)
    history = Transaction.consumption.get_last_two_weeks(self.item1.id)
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
    history = Transaction.consumption.get_last_two_weeks(
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

  def test_create_is_noop(self):
    serializer = ItemHistorySerializer(data={})
    serializer.create(validated_data={})

  def test_update_is_noop(self):
    serializer = ItemHistorySerializer(data={})
    serializer.update(instance={}, validated_data={})
