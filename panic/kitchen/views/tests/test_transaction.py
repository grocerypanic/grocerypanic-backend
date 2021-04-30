"""Test the Transaction API."""

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from ...models.transaction import Transaction
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
