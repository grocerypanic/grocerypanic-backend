"""Test the Transaction API."""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from ..models.transaction import Transaction
from ..serializers.transaction import TransactionSerializer
from .fixtures.transaction import TransactionTestHarness

TRANSACTION_URL = reverse("kitchen:transactions-list")


def transaction_query_url(query_kwargs={}):  # pylint: disable=W0102
  return '{}?{}'.format(TRANSACTION_URL, urlencode(query_kwargs))


class PublicItemTest(TestCase):
  """Test the public Transaction API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_create_login_required(self):
    payload = {}
    res = self.client.post(TRANSACTION_URL, data=payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateItemTest(TransactionTestHarness):
  """Test the authorized Transaction API"""
  item2 = None
  user2 = None

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.today = timezone.now()

    cls.serializer_data = {'item': cls.item1.id, 'quantity': 3}
    cls.object_def1 = {
        'user': cls.user1,
        'date_object': timezone.now(),
        'item': cls.item1,
        'quantity': 5
    }
    cls.object_def2 = {
        'user': cls.user1,
        'date_object': timezone.now() + timezone.timedelta(seconds=1),
        'item': cls.item1,
        'quantity': 5
    }
    cls.object_def3 = {
        'user': cls.user1,
        'date_object': timezone.now() + timezone.timedelta(seconds=2),
        'item': cls.item2,
        'quantity': 5
    }
    cls.object_def4 = {
        'user': cls.user1,
        'date_object': timezone.now() - timezone.timedelta(days=11),
        'item': cls.item1,
        'quantity': 5
    }

  @classmethod
  def setUpTestData(cls):
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']
    super().setUpTestData()

  def setUp(self):
    super().setUp()
    self.item1.quantity = 3
    self.item1.save()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  @freeze_time("2014-01-01")
  def test_create_transaction(self):
    """Test creating a transaction."""
    res = self.client.post(TRANSACTION_URL, data=self.serializer_data)

    items = Transaction.objects.all()
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    assert len(items) == 1
    transaction = items[0]

    self.assertEqual(transaction.user.id, self.user1.id)
    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, timezone.now())
    self.assertEqual(transaction.quantity, self.serializer_data['quantity'])
    assert transaction.item.quantity == 6  # The modified value

  def test_list_all_transactions_without_item_filter(self):
    """Test retrieving a list of all user transactions."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def3)

    res = self.client.get(transaction_query_url())

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  @freeze_time("2020-01-14")
  def test_list_all_transactions(self):
    """Test retrieving a list of all user transactions."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)

    res = self.client.get(transaction_query_url({"item": self.item1.id}))

    items = Transaction.objects.all().order_by("-datetime")
    serializer = TransactionSerializer(items, many=True)

    assert len(items) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_item_filter(self):
    """Test retrieving a list of transactions by item id."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def3)

    res = self.client.get(transaction_query_url({"item": self.item1.id}))

    items = Transaction.objects.filter(item=self.item1).order_by("-datetime")
    serializer = TransactionSerializer(items, many=True)

    assert len(items) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_another_item_filter(self):
    """Test retrieving a list of transactions by item id."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def3)

    res = self.client.get(transaction_query_url({"item": self.item2.id}))

    items = Transaction.objects.filter(item=self.item2).order_by("-datetime")
    serializer = TransactionSerializer(items, many=True)

    assert len(items) == 1
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_history_manual_value(self):
    """Test retrieving the last 10 days worth of transactions."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def4)

    res = self.client.get(
        transaction_query_url({
            "item": self.item1.id,
            "history": 10
        })
    )
    self.assertEqual(len(res.data), 2)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_history_default_value(self):
    """Test retrieving the default number of days of transactions."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def4)

    res = self.client.get(transaction_query_url({
        "item": self.item1.id,
    }))
    self.assertEqual(len(res.data), 3)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_history_invalid_value(self):
    """Test fall back to default when an invalid number of days is specified."""
    self.create_test_instance(**self.object_def1)
    self.create_test_instance(**self.object_def2)
    self.create_test_instance(**self.object_def4)

    res = self.client.get(
        transaction_query_url({
            "item": self.item1.id,
            "history": "not a number"
        })
    )
    self.assertEqual(len(res.data), 3)
