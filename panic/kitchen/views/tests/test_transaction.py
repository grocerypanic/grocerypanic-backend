"""Test the Transaction API."""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from utilities.views.deprecation import DEPRECATED_WARNING
from ...models.transaction import Transaction
from ...serializers.transaction import TransactionSerializer
from ..transaction import TRANSACTION_LIST_SUNSET
from .fixtures.fixtures_transaction import TransactionViewSetHarness

TRANSACTION_URL = reverse("v1:transactions-list")


# pylint: disable=dangerous-default-value
def transaction_query_url(query_kwargs={}):
  return '{}?{}'.format(TRANSACTION_URL, urlencode(query_kwargs))


class PublicTransactionTest(TestCase):
  """Test the public Transaction API."""

  def setUp(self):
    self.client = APIClient()

  def test_create_login_required(self):
    payload = {}
    res = self.client.post(TRANSACTION_URL, data=payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTransactionTest(TransactionViewSetHarness):
  """Test the authorized Transaction API."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  @freeze_time("2014-01-01")
  def test_create_transaction(self):
    res = self.client.post(TRANSACTION_URL, data=self.serializer_data)

    items = Transaction.objects.all()
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    assert len(items) == 1
    transaction = items[0]

    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, timezone.now())
    self.assertEqual(transaction.quantity, self.serializer_data['quantity'])
    assert transaction.item.quantity == transaction.quantity

  def test_list_all_transactions_without_item_filter(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)
    self.create_test_instance(**self.transaction_two_seconds_another_item)

    res = self.client.get(transaction_query_url())

    self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

  @freeze_time("2020-01-14")
  def test_list_all_transactions(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)

    res = self.client.get(transaction_query_url({"item": self.item1.id}))

    items = Transaction.objects.all().order_by("-datetime")
    serializer = TransactionSerializer(items, many=True)

    assert len(items) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  @freeze_time("2020-01-14")
  def test_list_all_transactions_ensure_deprecated(self):
    res = self.client.get(transaction_query_url({"item": self.item1.id}))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res['Deprecation'], str(TRANSACTION_LIST_SUNSET))
    self.assertEqual(res['Warning'], DEPRECATED_WARNING)
    self.assertEqual(res['Sunset'], str(TRANSACTION_LIST_SUNSET))

  @freeze_time("2020-01-14")
  def test_list_transactions_by_item_filter(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)
    self.create_test_instance(**self.transaction_two_seconds_another_item)

    res = self.client.get(transaction_query_url({"item": self.item1.id}))

    items = Transaction.objects.filter(item=self.item1).order_by("-datetime")
    serializer = TransactionSerializer(items, many=True)

    assert len(items) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_history_manual_value(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)
    self.create_test_instance(**self.transaction_eleven_days_ago)

    res = self.client.get(
        transaction_query_url({
            "item": self.item1.id,
            "history": 10
        })
    )
    self.assertEqual(len(res.data['results']), 2)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_history_default_value(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)
    self.create_test_instance(**self.transaction_eleven_days_ago)

    res = self.client.get(transaction_query_url({
        "item": self.item1.id,
    }))
    self.assertEqual(len(res.data['results']), 3)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_history_invalid_value(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)
    self.create_test_instance(**self.transaction_eleven_days_ago)

    res = self.client.get(
        transaction_query_url({
            "item": self.item1.id,
            "history": "not a number"
        })
    )
    self.assertEqual(len(res.data['results']), 3)

  @freeze_time("2020-01-14")
  def test_list_transactions_ensure_pagination_active(self):
    self.create_test_instance(**self.transaction_now)

    res = self.client.get(transaction_query_url({
        "item": self.item1.id,
    }))
    self.assertIsNone(res.data['next'])
    self.assertIsNone(res.data['previous'])
    self.assertIsNotNone(res.data['results'])


class PrivateTransactionAnotherUser(TransactionViewSetHarness):
  """Test the authorized Transaction API, as another user."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  @freeze_time("2014-01-01")
  def test_create_transaction(self):
    res = self.client.post(TRANSACTION_URL, data=self.serializer_data)

    items = Transaction.objects.all()
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    assert len(items) == 1
    transaction = items[0]

    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, timezone.now())
    self.assertEqual(transaction.quantity, self.serializer_data['quantity'])
    assert transaction.item.quantity == transaction.quantity

  @freeze_time("2014-01-01")
  def test_create_transaction_item_owned_by_another_user(self):
    res = self.client.post(
        TRANSACTION_URL,
        data=self.serializer_data_wrong_item,
    )

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  @freeze_time("2020-01-14")
  def test_list_transactions_by_item_of_different_user(self):
    self.create_test_instance(**self.transaction_now)
    self.create_test_instance(**self.transaction_one_second)
    self.create_test_instance(**self.transaction_two_seconds_another_item)

    res = self.client.get(transaction_query_url({"item": self.item2.id}))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])