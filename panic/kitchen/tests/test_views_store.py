"""Test the Store API."""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APIClient

from ..models.store import Store
from ..serializers.store import StoreSerializer
from .fixtures.store import StoreTestHarness

STORE_URL = reverse("kitchen:stores-list")


class AnotherUserTestHarness(StoreTestHarness):

  @classmethod
  def create_data_hook(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']


def store_url_with_params(query_kwargs):
  return '{}?{}'.format(STORE_URL, urlencode(query_kwargs))


class PublicStoreTest(TestCase):
  """Test the public Store API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_login_required(self):
    """Test that login is required for retrieving shelves."""
    res = self.client.get(STORE_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_create_login_required(self):
    payload = {"name": "Loblaws"}
    res = self.client.post(STORE_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateStoreTest(StoreTestHarness):
  """Test the authorized Store API"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def test_list_stores(self):
    """Test retrieving a list of stores."""
    self.create_test_instance(user=self.user1, name="No Frills")
    self.create_test_instance(user=self.user1, name="Loblaws")

    res = self.client.get(STORE_URL)

    shelves = Store.objects.all().order_by("index")
    serializer = StoreSerializer(shelves, many=True)

    assert len(shelves) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_stores_paginated_correctly(self):
    """Test that retrieving a list of stores is limited correctly."""
    for index in range(0, 11):
      data = "storename" + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(store_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 10)
    self.assertIsNotNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_stores_paginated_overidden_correctly(self):
    """Test retrieving a the full list of stores."""
    for index in range(0, 11):
      data = 'storesname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(
        store_url_with_params({
            "page_size": 10,
            settings.PAGINATION_OVERRIDE_PARAM: "true"
        })
    )
    self.assertEqual(len(res.data), 11)

  def test_delete_store(self):
    """Test deleting a store."""
    delete = self.create_test_instance(user=self.user1, name="A&P")
    self.create_test_instance(user=self.user1, name="Beckers")

    res_delete = self.client.delete(STORE_URL + str(delete.id) + '/')
    res_get = self.client.get(STORE_URL)

    shelves = Store.objects.all().order_by("index")
    serializer = StoreSerializer(shelves, many=True)

    assert len(shelves) == 1
    self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(res_get.status_code, status.HTTP_200_OK)
    self.assertEqual(res_get.data['results'], serializer.data)

  def test_create_store(self):
    """Test creating a store."""
    data = {"name": "Shoppers Drugmart"}

    res = self.client.post(STORE_URL, data=data)

    shelves = Store.objects.all().order_by("index")

    assert len(shelves) == 1
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    self.assertEqual(shelves[0].name, data['name'])


class PrivateStoreTestAnotherUser(AnotherUserTestHarness):
  """Test the authorized Store API from Another User"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  def test_list_stores(self):
    """Test retrieving a list of stores."""
    self.create_test_instance(user=self.user1, name="No Frills")
    self.create_test_instance(user=self.user1, name="Loblaws")

    res = self.client.get(STORE_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_list_stores_paginated_correctly(self):
    """Test that retrieving a list of stores is limited correctly."""
    for index in range(0, 11):
      data = "storename" + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(store_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 0)
    self.assertIsNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_stores_paginated_overidden_correctly(self):
    """Test retrieving a the full list of stores."""
    for index in range(0, 11):
      data = 'storesname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(
        store_url_with_params({
            "page_size": 10,
            settings.PAGINATION_OVERRIDE_PARAM: "true"
        })
    )
    self.assertEqual(len(res.data), 0)

  def test_delete_store(self):
    """Test deleting a store."""
    delete = self.create_test_instance(user=self.user1, name="A&P")
    self.create_test_instance(user=self.user1, name="Beckers")

    res_delete = self.client.delete(STORE_URL + str(delete.id) + '/')
    self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)
