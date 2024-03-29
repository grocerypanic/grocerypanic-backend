"""Test the V1 kitchen ItemActivity API."""

from datetime import timedelta

import faker
from django.urls import reverse
from django.utils.timezone import now
from freezegun import freeze_time
from rest_framework import status

from .bases import APICrudTestHarness, APICrudTestHarnessUnauthorized


@freeze_time("2020-01-14")
class ItemConsumptionAPICrudTest(APICrudTestHarness):
  """Test the V1 Kitchen ItemActivity API Authorized endpoints."""

  test_view = 'v1:items-activity-pk'
  transaction_view = 'v1:transactions-list'
  item_view = 'v1:items-supplementary-list'
  store_view = 'v1:stores-supplementary-list'
  shelf_view = 'v1:shelves-supplementary-list'

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.shelf_view = reverse(cls.shelf_view)
    cls.store_view = reverse(cls.store_view)
    cls.item_view = reverse(cls.item_view)
    cls.transaction_view = reverse(cls.transaction_view)

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

  def _data_generate_transaction(self, item, offset, quantity):
    return {
        'item': item,
        'datetime': now() + timedelta(days=offset),
        'quantity': quantity,
    }

  def _data_generate_transaction_dataset(self, item_id):
    transactions_data = list()
    transactions_data.append(self._data_generate_transaction(item_id, -20, 100))
    transactions_data.append(self._data_generate_transaction(item_id, -5, -5))
    transactions_data.append(self._data_generate_transaction(item_id, -5, -5))
    transactions_data.append(self._data_generate_transaction(item_id, -3, -1))
    transactions_data.append(self._data_generate_transaction(item_id, -2, 10))
    transactions_data.append(self._data_generate_transaction(item_id, -1, -1))

    return transactions_data

  def test_report(self):
    item_id = self._create_dependencies()
    transactions_data = self._data_generate_transaction_dataset(item_id)
    transactions_responses = []

    for data in transactions_data:
      response = self._api_create(data, self.transaction_view)
      self.assertEqual(response.status_code, status.HTTP_201_CREATED)
      transactions_responses.append(response)

    list_response = self._api_list(self.view(item_id))
    self.assertEqual(list_response.status_code, status.HTTP_200_OK)

    def as_user_date(datetime_object):
      return str(datetime_object.astimezone(self.user.timezone).date())

    self.assertDictEqual(
        list_response.json(),
        {
            'id':
                item_id,
            'activity_first':
                (transactions_data[0]['datetime'].isoformat()[:-6] + 'Z'),
            'recent_activity': {
                'activity_last_two_weeks': [
                    {
                        'date': as_user_date(now()),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(transactions_data[5]['datetime']),
                        'change': transactions_data[5]['quantity'],
                    },
                    {
                        'date': as_user_date(transactions_data[4]['datetime']),
                        'change': transactions_data[4]['quantity'],
                    },
                    {
                        'date': as_user_date(transactions_data[3]['datetime']),
                        'change': transactions_data[3]['quantity'],
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=4)),
                        'change': 0,
                    },
                    {
                        'date':
                            as_user_date(transactions_data[2]['datetime']),
                        'change': (
                            transactions_data[2]['quantity'] +
                            transactions_data[1]['quantity']
                        ),
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=6)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=7)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=8)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=9)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=10)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=11)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=12)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=13)),
                        'change': 0,
                    },
                    {
                        'date': as_user_date(now() - timedelta(days=14)),
                        'change': 0,
                    },
                ],
                'usage_current_month':
                    float(
                        abs(transactions_data[5]['quantity']) +
                        abs(transactions_data[3]['quantity']) +
                        abs(transactions_data[2]['quantity']) +
                        abs(transactions_data[1]['quantity'])
                    ),
                'usage_current_week':
                    float(abs(transactions_data[5]['quantity'])),
                'user_timezone':
                    str(self.user.timezone),
            },
            'usage_total':
                float(
                    abs(transactions_data[5]['quantity']) +
                    abs(transactions_data[3]['quantity']) +
                    abs(transactions_data[2]['quantity']) +
                    abs(transactions_data[1]['quantity'])
                ),
            'usage_avg_week':
                float(
                    abs(transactions_data[5]['quantity']) +
                    abs(transactions_data[3]['quantity']) +
                    abs(transactions_data[2]['quantity']) +
                    abs(transactions_data[1]['quantity'])
                ) / 3,
            'usage_avg_month':
                float(
                    abs(transactions_data[5]['quantity']) +
                    abs(transactions_data[3]['quantity']) +
                    abs(transactions_data[2]['quantity']) +
                    abs(transactions_data[1]['quantity'])
                ),
        },
    )


class ItemConsumption(APICrudTestHarnessUnauthorized):
  """Test the V1 Kitchen ItemActivity API Authorized endpoints anonymously."""

  test_view = 'v1:items-activity-pk'
  __test__ = True
  __non_pk_checks__ = False
  __pk_checks__ = True
