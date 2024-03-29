"""Test the Item API."""

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APIClient

from ...models.item import Item
from ...serializers.item import ItemSerializer
from .fixtures.fixtures_item import ItemViewSetTestHarness

ITEM_URL = reverse("v1:items-supplementary-list")


def item_url_with_params(query_kwargs):
  return '{}?{}'.format(ITEM_URL, urlencode(query_kwargs))


class PublicItemTest(TestCase):
  """Test the public Item API."""

  def setUp(self):
    self.client = APIClient()

  def test_login_required(self):
    res = self.client.get(ITEM_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_create_login_required(self):
    payload = {}
    res = self.client.post(ITEM_URL, data=payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_update_login_required(self):
    payload = {}
    res = self.client.put(ITEM_URL, data=payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateItemTest(ItemViewSetTestHarness):
  """Test the authorized Item API."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def test_list_items(self):
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL)

    items = Item.objects.all().order_by("_index")
    serializer = ItemSerializer(items, many=True)

    assert items.count() == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_items_order(self):
    item1 = self.create_test_instance(**self.data1)
    item2 = self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'][0]['name'], item1.name)
    self.assertEqual(res.data['results'][1]['name'], item2.name)

  def test_retrieve_single_item(self):
    item = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL + str(item.id) + "/")

    items = Item.objects.get(id=item.id)
    serializer = ItemSerializer(items)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_list_items_paginated_correctly(self):
    for index in range(0, 11):
      data = dict(self.data1)
      data['name'] += str(index)
      self.create_test_instance(**data)

    res = self.client.get(item_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 10)
    self.assertIsNotNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_items_by_store(self):
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"preferred_stores": self.store1.id})
    res = self.client.get(url)

    items = Item.objects.all().order_by("_index")
    serializer = ItemSerializer(
        items.filter(preferred_stores__in=[self.store1.id]), many=True
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_items_by_shelf(self):
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"shelf": self.shelf1.id})
    res = self.client.get(url)

    items = Item.objects.all().order_by("_index")
    serializer = ItemSerializer(items.filter(shelf=self.shelf1.id), many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_delete_item(self):
    delete = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res_delete = self.client.delete(ITEM_URL + str(delete.id) + '/')
    res_get = self.client.get(ITEM_URL)

    items = Item.objects.all().order_by("_index")
    serializer = ItemSerializer(items, many=True)

    assert len(items) == 1
    self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(res_get.status_code, status.HTTP_200_OK)
    self.assertEqual(res_get.data['results'], serializer.data)

  def test_create_item(self):
    res = self.client.post(ITEM_URL, data=self.serializer_data)

    items = Item.objects.all().order_by("_index")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    assert len(items) == 1
    item = items[0]

    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.expired, 0)
    self.assertFalse(item.has_partial_quantities)
    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.next_expiry_date, None)
    self.assertEqual(item.next_expiry_datetime, None)
    self.assertEqual(item.next_expiry_quantity, 0)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, 0)
    self.assertEqual(item.shelf.id, self.shelf1.id)
    self.assertEqual(item.shelf_life, self.serializer_data['shelf_life'])

    preferred_stores = item.preferred_stores.all()
    assert len(preferred_stores) == 1
    self.assertEqual(preferred_stores[0].id, self.store1.id)

  def test_update_item(self):
    original = self.create_test_instance(**self.data1)
    res = self.client.put(
        ITEM_URL + str(original.id) + '/', data=self.serializer_data
    )

    # Ensure the original object has wrong data
    self.assertNotEqual(original.name, self.serializer_data['name'])

    items = Item.objects.all().order_by("_index")
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    assert len(items) == 1
    item = items[0]

    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.expired, 0)
    self.assertFalse(item.has_partial_quantities)
    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.next_expiry_date, None)
    self.assertEqual(item.next_expiry_datetime, None)
    self.assertEqual(item.next_expiry_quantity, 0)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, 0)
    self.assertEqual(item.shelf.id, self.shelf1.id)
    self.assertEqual(item.shelf_life, self.serializer_data['shelf_life'])

    preferred_stores = item.preferred_stores.all()
    assert len(preferred_stores) == 1
    self.assertEqual(preferred_stores[0].id, self.store1.id)

    # Update Object and Confirm It is Updated
    original.refresh_from_db()
    self.assertEqual(original.name, self.serializer_data['name'])


class PrivateItemTestAnotherUser(ItemViewSetTestHarness):
  """Test the authorized Item API with another user."""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  def test_list_items(self):
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_retrieve_single_item(self):
    item = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL + str(item.id) + "/")
    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_list_items_paginated_correctly(self):
    for index in range(0, 11):
      data = dict(self.data1)
      data['name'] += str(index)
      self.create_test_instance(**data)

    res = self.client.get(item_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 0)
    self.assertIsNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_items_by_store(self):
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"preferred_stores": self.store1.id})
    res = self.client.get(url)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_list_items_by_shelf(self):
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"shelf": self.shelf1.id})
    res = self.client.get(url)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_delete_item(self):
    delete = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res_delete = self.client.delete(ITEM_URL + str(delete.id) + '/')
    self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)

  def test_update_item(self):
    original = self.create_test_instance(**self.data1)
    res = self.client.put(
        ITEM_URL + str(original.id) + '/', data=self.serializer_data
    )

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_create_item_wrong_user(self):
    res = self.client.post(ITEM_URL, data=self.serializer_data)

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_create_item_wrong_shelf(self):
    res = self.client.post(ITEM_URL, data=self.serializer_data_wrong_shelf)

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_create_item_wrong_store(self):
    res = self.client.post(ITEM_URL, data=self.serializer_data_wrong_store)

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
