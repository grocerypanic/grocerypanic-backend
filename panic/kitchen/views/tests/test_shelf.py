"""Test the Shelf API."""

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APIClient

from ...models.shelf import Shelf
from ...serializers.shelf import ShelfSerializer
from ...tests.fixtures.fixtures_shelf import ShelfTestHarness
from .fixtures.fixtures_item import ItemViewSetTestHarness
from .fixtures.fixtures_shelf import AnotherUserTestHarness

SHELF_URL = reverse("v1:shelves-supplementary-list")


def shelf_url_with_params(query_kwargs):
  return '{}?{}'.format(SHELF_URL, urlencode(query_kwargs))


class PublicShelfTest(TestCase):
  """Test the public Shelf API."""

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    res = self.client.get(SHELF_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_create_login_required(self):
    payload = {"name": "Pantry"}
    res = self.client.post(SHELF_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateShelfTest(ShelfTestHarness):
  """Test the authorized Shelf API."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def test_list_shelves(self):
    self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res = self.client.get(SHELF_URL)

    shelves = Shelf.objects.all().order_by("_index")
    serializer = ShelfSerializer(shelves, many=True)

    assert len(shelves) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_shelves_order(self):
    item1 = self.create_test_instance(name="ZZZZZ", user=self.user1)
    item2 = self.create_test_instance(name="AAAAA", user=self.user1)

    res = self.client.get(SHELF_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    assert len(res.data['results']) == 2
    self.assertEqual(res.data['results'][0]['name'], item2.name)
    self.assertEqual(res.data['results'][1]['name'], item1.name)

  def test_list_shelves_paginated_correctly(self):
    for index in range(0, 11):
      data = 'shelfname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(shelf_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 10)
    self.assertIsNotNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_shelves_paginated_overridden_correctly(self):
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
    delete = self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res_delete = self.client.delete(SHELF_URL + str(delete.id) + '/')
    res_get = self.client.get(SHELF_URL)

    shelves = Shelf.objects.all().order_by("_index")
    serializer = ShelfSerializer(shelves, many=True)

    assert len(shelves) == 1
    self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(res_get.status_code, status.HTTP_200_OK)
    self.assertEqual(res_get.data['results'], serializer.data)

  def test_create_shelf(self):
    data = {"name": "Refrigerator"}

    res = self.client.post(SHELF_URL, data=data)

    shelves = Shelf.objects.all().order_by("_index")

    assert len(shelves) == 1
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    self.assertEqual(shelves[0].name, data['name'])


class PrivateShelfTestInUse(ItemViewSetTestHarness):
  """Test the authorized Shelf API with existing items referencing a Shelf."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def test_delete_referenced_shelf(self):
    delete = self.create_test_instance(**self.data1)
    count1 = Shelf.objects.all().order_by("_index").count()

    res = self.client.delete(SHELF_URL + str(delete.shelf.id) + '/')

    count2 = Shelf.objects.all().order_by("_index").count()

    assert count1 == count2
    self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)


class PrivateShelfTestAnotherUser(AnotherUserTestHarness):
  """Test the authorized Shelf API from another user."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  def test_list_shelves(self):
    self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res = self.client.get(SHELF_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_list_shelves_paginated_correctly(self):
    for index in range(0, 11):
      data = 'shelfname' + str(index)
      self.create_test_instance(user=self.user1, name=data)

    res = self.client.get(shelf_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 0)
    self.assertIsNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_shelves_paginated_overridden_correctly(self):
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
    delete = self.create_test_instance(user=self.user1, name="Refrigerator")
    self.create_test_instance(user=self.user1, name="Pantry")

    res_delete = self.client.delete(SHELF_URL + str(delete.id) + '/')
    self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)
