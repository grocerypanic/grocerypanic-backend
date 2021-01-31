"""Test the Transaction API."""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from ..serializers.transaction import TransactionConsumptionHistorySerializer
from .fixtures.django import MockRequest
from .fixtures.transaction import TransactionTestHarness


def transaction_query_url(item):  # pylint: disable=W0102
  return reverse("kitchen:transaction-consumption-history-detail", args=[item])


class PublicTransactionConsumptionHistoryTest(TestCase):
  """Test the public Transaction Consumption History API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_get_login_required(self):
    res = self.client.get(transaction_query_url(0))

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTransactionConsumptionHistoryTest(TransactionTestHarness):
  """Test the authorized Transaction Consumption History API"""

  @classmethod
  @freeze_time("2020-01-14")
  def create_transactions_hook(cls):

    cls.serializer_data = {'item': cls.item.id, 'quantity': 3}
    cls.today = timezone.now()
    cls.object_def1 = {
        'user': cls.user,
        'date_object': cls.today,
        'item': cls.item,
        'quantity': -5
    }
    cls.object_def2 = {
        'user': cls.user,
        'date_object': cls.today - timezone.timedelta(days=5),
        'item': cls.item,
        'quantity': -5
    }
    cls.object_def3 = {
        'user': cls.user,
        'date_object': cls.today - timezone.timedelta(days=16),
        'item': cls.item,
        'quantity': -5
    }

    cls.MockRequest = MockRequest(cls.user)

  def setUp(self):
    self.objects = list()
    self.item.quantity = 2000
    self.item.save()
    self.client = APIClient()
    self.client.force_authenticate(self.user)
    self.populate_history()

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()

  def populate_history(self):
    self.sample_transaction(**self.object_def1)
    self.sample_transaction(**self.object_def2)
    self.sample_transaction(**self.object_def3)

  @freeze_time("2020-01-14")
  def test_get_item_history(self):
    """Test retrieving consumption history for the last two weeks"""
    res = self.client.get(transaction_query_url(self.item.id))
    serializer = TransactionConsumptionHistorySerializer(
        {
            "item_id": self.item,
        },
        context={
            'request': self.MockRequest,
        },
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['consumption_last_two_weeks'],
        serializer.data['consumption_last_two_weeks']
    )

  @freeze_time("2020-01-14")
  def test_first_transaction(self):
    """Test identifying the first transaction date of a consumption event."""
    res = self.client.get(transaction_query_url(self.item.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['first_consumption_date'], self.object_def3['date_object']
    )

  @freeze_time("2020-01-14")
  def test_total_consumption(self):
    """Test identifying the total consumption of a user's item."""
    res = self.client.get(transaction_query_url(self.item.id))
    total_consumption = abs(
        self.object_def1['quantity'] + self.object_def2['quantity'] +
        self.object_def3['quantity']
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['total_consumption'], total_consumption)
