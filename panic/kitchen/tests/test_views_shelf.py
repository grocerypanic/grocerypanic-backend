"""Test the Shelf API."""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APIClient

from ..models.shelf import Shelf
from ..serializers.shelf import ShelfSerializer
from .fixtures.shelf import ShelfTestHarness

SHELF_URL = reverse("kitchen:shelves-list")


class AnotherUserTestHarness(ShelfTestHarness):

  @classmethod
  def create_data_hook(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']


def shelf_url_with_params(query_kwargs):
  return '{}?{}'.format(SHELF_URL, urlencode(query_kwargs))


class PublicShelfTest(TestCase):
  """Test the public Shelf API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_login_required(self):
    """Test that login is required for retrieving shelves."""
    res = self.client.get(SHELF_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_create_login_required(self):
    payload = {"name": "Pantry"}
    res = self.client.post(SHELF_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateShelfTest(ShelfTestHarness):
  """Test the authorized Shelf API"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def test_list_shelves(self):
    """Test retrieving a list of shelves."""
    self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res = self.client.get(SHELF_URL)

    shelves = Shelf.objects.all().order_by("index")
    serializer = ShelfSerializer(shelves, many=True)

    assert len(shelves) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_shelves_paginated_correctly(self):
    """Test retrieving a list of shelves is paginated correctly."""
    for index in range(0, 11):
      data = 'shelfname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(shelf_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 10)
    self.assertIsNotNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_shelves_paginated_overidden_correctly(self):
    """Test retrieving a the full list of shelves."""
    for index in range(0, 11):
      data = 'shelfname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(
        shelf_url_with_params({
            "page_size": 10,
            settings.PAGINATION_OVERRIDE_PARAM: "true"
        })
    )
    self.assertEqual(len(res.data), 11)

  def test_delete_shelf(self):
    """Test deleting a shelf."""
    delete = self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res_delete = self.client.delete(SHELF_URL + str(delete.id) + '/')
    res_get = self.client.get(SHELF_URL)

    shelves = Shelf.objects.all().order_by("index")
    serializer = ShelfSerializer(shelves, many=True)

    assert len(shelves) == 1
    self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(res_get.status_code, status.HTTP_200_OK)
    self.assertEqual(res_get.data['results'], serializer.data)

  def test_create_shelf(self):
    """Test creating a shelf."""
    data = {"name": "Refrigerator"}

    res = self.client.post(SHELF_URL, data=data)

    shelves = Shelf.objects.all().order_by("index")

    assert len(shelves) == 1
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    self.assertEqual(shelves[0].name, data['name'])


class PrivateShelfTestAnotherUser(AnotherUserTestHarness):
  """Test the authorized Shelf API from Another User"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  def test_list_shelves(self):
    """Test retrieving a list of shelves."""
    self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res = self.client.get(SHELF_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_list_shelves_paginated_correctly(self):
    """Test retrieving a list of shelves is paginated correctly."""
    for index in range(0, 11):
      data = 'shelfname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(shelf_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 0)
    self.assertIsNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_shelves_paginated_overidden_correctly(self):
    """Test retrieving a the full list of shelves."""
    for index in range(0, 11):
      data = 'shelfname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(
        shelf_url_with_params({
            "page_size": 10,
            settings.PAGINATION_OVERRIDE_PARAM: "true"
        })
    )
    self.assertEqual(len(res.data), 0)

  def test_delete_shelf(self):
    """Test deleting a shelf."""
    delete = self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res_delete = self.client.delete(SHELF_URL + str(delete.id) + '/')
    self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)
