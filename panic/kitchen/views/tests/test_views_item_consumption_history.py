"""Test the Transaction API."""

import pytz
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from ...tests.fixtures.django import MockRequest
from ...tests.fixtures.transaction import TransactionTestHarness
from ..item import ItemConsumptionHistorySerializer

CONSUMPTION_HISTORY_VIEW = "v1:item-consumption-detail"


class PrivateTCHTestHarness(TransactionTestHarness):

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer_data = {'item': cls.item1.id, 'quantity': 3}
    cls.today = timezone.now()
    cls.object_def1 = {
        'user': cls.user1,
        'date_object': cls.today,
        'item': cls.item1,
        'quantity': -5
    }
    cls.object_def2 = {
        'user': cls.user1,
        'date_object': cls.today - timezone.timedelta(days=5),
        'item': cls.item1,
        'quantity': -5
    }
    cls.object_def3 = {
        'user': cls.user1,
        'date_object': cls.today - timezone.timedelta(days=16),
        'item': cls.item1,
        'quantity': -5
    }

    cls.MockRequest = MockRequest(cls.user1)

  def setUp(self):
    super().setUp()
    self.item1.quantity = 2000
    self.item1.save()
    self.populate_history()

  def populate_history(self):
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def3)


def item_pk_url(item):
  return reverse(CONSUMPTION_HISTORY_VIEW, args=[item])


def item_query_url(item, query_kwargs={}):  # pylint: disable=W0102
  return '{}?{}'.format(item_pk_url(item), urlencode(query_kwargs))


class PublicTCHTest(TestCase):
  """Test the public Transaction Consumption History API"""

  def setUp(self):
    self.client = APIClient()

  def test_get_login_required(self):
    res = self.client.get(item_pk_url(0))

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTCHTest(PrivateTCHTestHarness):
  """Test the authorized TCH API"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  @freeze_time("2020-01-14")
  def test_get_item_history(self):
    """Test retrieving consumption history for the last two weeks"""
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
  def test_first_transaction(self):
    """Test identifying the first transaction date of a consumption event."""
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['first_consumption_date'], self.object_def3['date_object']
    )

  @freeze_time("2020-01-14")
  def test_total_consumption(self):
    """Test identifying the total consumption of a user's item."""
    res = self.client.get(item_pk_url(self.item1.id))
    total_consumption = abs(
        self.object_def1['quantity'] + self.object_def2['quantity'] +
        self.object_def3['quantity']
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['total_consumption'], total_consumption)

  def test_specify_timezone(self):
    """Test pagination is turned on for this endpoint"""
    test_timezone = "Asia/Hong_Kong"
    res = self.client.get(
        item_query_url(
            self.item1.id,
            query_kwargs={"timezone": test_timezone},
        )
    )

    self.assertEqual(
        res.data['first_consumption_date'],
        self.object_def3['date_object'].astimezone(
            pytz.timezone(test_timezone)
        )
    )

  def test_specify_illegal_timezone(self):
    """Test pagination is turned on for this endpoint"""
    test_timezone = "Not A Valid Timezone"
    res = self.client.get(
        item_query_url(
            self.item1.id,
            query_kwargs={"timezone": test_timezone},
        )
    )

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateTCHTestAnotherUser(PrivateTCHTestHarness):
  """Test the authorized TCH API from Another User"""

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
    """Test retrieving consumption history for the last two weeks"""
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
