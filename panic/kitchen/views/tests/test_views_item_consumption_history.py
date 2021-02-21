"""Test the Transaction API."""

import pytz
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from ...tests.fixtures.fixtures_django import MockRequest, deserialize_date
from ...tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..item import ItemConsumptionHistorySerializer

CONSUMPTION_HISTORY_VIEW = "v1:item-consumption-detail"


class PrivateTCHTestHarness(TransactionTestHarness):
  """Extend the transaction test harness by adding transaction test data."""

  mute_signals = False

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer_data = {'item': cls.item1.id, 'quantity': 3}
    cls.today = timezone.now()
    cls.five_days_ago = cls.today - timezone.timedelta(days=5)
    cls.sixteen_days_ago = cls.today - timezone.timedelta(days=16)

    cls.initial_transaction = {
        'user': cls.user1,
        'date_object': cls.today - timezone.timedelta(days=365),
        'item': cls.item1,
        'quantity': 200
    }
    cls.transaction_today = {
        'user': cls.user1,
        'date_object': cls.today,
        'item': cls.item1,
        'quantity': -5
    }
    cls.transaction_5_days_ago = {
        'user': cls.user1,
        'date_object': cls.five_days_ago,
        'item': cls.item1,
        'quantity': -5
    }
    cls.transaction_16_days_ago = {
        'user': cls.user1,
        'date_object': cls.sixteen_days_ago,
        'item': cls.item1,
        'quantity': -5
    }

    cls.MockRequest = MockRequest(cls.user1)

  def setUp(self):
    super().setUp()
    self.reset_item1()
    self.populate_history()

  def populate_history(self):
    self.create_test_instance(**self.initial_transaction)
    self.create_test_instance(**self.transaction_today)
    self.create_test_instance(**self.transaction_5_days_ago)
    self.create_test_instance(**self.transaction_16_days_ago)


def item_pk_url(item):
  return reverse(CONSUMPTION_HISTORY_VIEW, args=[item])


# pylint: disable=dangerous-default-value
def item_query_url(item, query_kwargs={}):
  return '{}?{}'.format(item_pk_url(item), urlencode(query_kwargs))


class PublicTCHTest(TestCase):
  """Test the public TCH (Transaction Consumption History) API."""

  def setUp(self):
    self.client = APIClient()

  def test_get_login_required(self):
    res = self.client.get(item_pk_url(0))

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTCHTest(PrivateTCHTestHarness):
  """Test the authorized TCH (Transaction Consumption History) API."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  @freeze_time("2020-01-14")
  def test_get_item_history(self):
    res = self.client.get(item_pk_url(self.item1.id))
    serializer = ItemConsumptionHistorySerializer(
        self.item1,
        data={},
        context={
            'request': self.MockRequest,
        },
    )
    serializer.is_valid(raise_exception=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['consumption_last_two_weeks'],
        serializer.data['consumption_last_two_weeks']
    )

  @freeze_time("2020-01-14")
  def test_get_item_history_order(self):
    res = self.client.get(item_pk_url(self.item1.id))
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    assert len(res.data['consumption_last_two_weeks']) == 2

    self.assertEqual(
        deserialize_date(res.data['consumption_last_two_weeks'][0]['date']),
        self.today.date()
    )
    self.assertEqual(
        deserialize_date(res.data['consumption_last_two_weeks'][1]['date']),
        self.five_days_ago.date()
    )

  @freeze_time("2020-01-14")
  def test_first_transaction(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['first_consumption_date'],
        self.transaction_16_days_ago['date_object']
    )

  @freeze_time("2020-01-14")
  def test_total_consumption(self):
    res = self.client.get(item_pk_url(self.item1.id))
    total_consumption = abs(
        self.transaction_today['quantity'] +
        self.transaction_5_days_ago['quantity'] +
        self.transaction_16_days_ago['quantity']
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['total_consumption'], total_consumption)

  def test_specify_timezone(self):
    test_timezone = "Asia/Hong_Kong"
    res = self.client.get(
        item_query_url(
            self.item1.id,
            query_kwargs={"timezone": test_timezone},
        )
    )

    self.assertEqual(
        res.data['first_consumption_date'],
        self.transaction_16_days_ago['date_object'].astimezone(
            pytz.timezone(test_timezone)
        )
    )

  def test_specify_illegal_timezone(self):
    test_timezone = "Not A Valid Timezone"
    res = self.client.get(
        item_query_url(
            self.item1.id,
            query_kwargs={"timezone": test_timezone},
        )
    )

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateTCHTestAnotherUser(PrivateTCHTestHarness):
  """Test the authorized TCH API from another user."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    super().create_data_hook()
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  @freeze_time("2020-01-14")
  def test_get_item_history(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
