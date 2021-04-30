"""Test the V1 kitchen Transaction API."""

import faker
import pytz
from django.urls import reverse
from rest_framework import status

from kitchen.models.transaction import Transaction
from .bases import APICrudTestHarness, APICrudTestHarnessUnauthorized


class TransactionAPICrudTest(APICrudTestHarness):
  """Test the V1 Kitchen Transaction API Authorized endpoints."""

  test_view = 'v1:transactions-list'
  item_view = 'v1:items-list'
  store_view = 'v1:stores-list'
  shelf_view = 'v1:shelves-list'

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.store_view = reverse(cls.store_view)
    cls.shelf_view = reverse(cls.shelf_view)
    cls.item_view = reverse(cls.item_view)

    cls.test_name = 'test_item_1'
    cls.faker = faker.Faker()

  def setUp(self):
    self._authorize()

  def _create_dependencies(self, index=1):
    shelf_data = {"name": f"test_shelf_{index}"}
    store_data = {"name": f"test_store_{index}"}

    shelf_response = self._api_create(shelf_data, self.shelf_view)
    shelf_id = shelf_response.json()['id']
    self.assertEqual(shelf_response.status_code, status.HTTP_201_CREATED)

    store_response = self._api_create(store_data, self.store_view)
    store_id = store_response.json()['id']
    self.assertEqual(store_response.status_code, status.HTTP_201_CREATED)

    item_data = self._data_generate_item(shelf_id, store_id)
    item_response = self._api_create(item_data, self.item_view)
    self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)

    return item_response.json()['id']

  def _data_generate_item(self, shelf_id=None, store_id=None):
    return {
        'has_partial_quantities': True,
        'name': self.faker.lexify(text='??????????'),
        'shelf_life': self.faker.numerify(text='###'),
        'shelf': shelf_id,
        'preferred_stores': [store_id],
        'price': float(self.faker.numerify(text='###.##')),
        'quantity': float(self.faker.numerify(text='###.##')),
    }

  def _data_generate_transaction(self, item):
    return {
        'item':
            item,
        'datetime':
            self.faker.date_time_between(
                tzinfo=pytz.timezone('America/Toronto'),
                start_date="-10d",
            ),
        'quantity':
            float(self.faker.numerify(text='###.#')),
    }

  def _data_generate_item_with_dependencies(self, index=1):
    item_id = self._create_dependencies(index)
    transaction_data = self._data_generate_transaction(item_id)
    return transaction_data, item_id

  def test_create(self):
    item_id = self._create_dependencies()
    transaction_data = self._data_generate_transaction(item_id)

    transaction_response = self._api_create(transaction_data, self.view)
    self.assertEqual(transaction_response.status_code, status.HTTP_201_CREATED)

    Transaction.objects.get(**transaction_response.json())

  def test_list(self):
    response = self.client.get(self._build_url(self.view))
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_delete(self):
    response = self.client.delete(self._build_url(self.view))
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_patch(self):
    response = self.client.patch(self._build_url(self.view))
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_put(self):
    response = self.client.put(self._build_url(self.view))
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class TransactionCrudTestUnauthorized(APICrudTestHarnessUnauthorized):
  """Test the V1 Kitchen Transaction API Authorized endpoints anonymously."""

  test_view = 'v1:transactions-list'
  __test__ = True
  __pk_checks__ = False
