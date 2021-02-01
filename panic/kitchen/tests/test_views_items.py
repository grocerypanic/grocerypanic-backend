"""Test the Item API."""

from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APIClient

from ..models.item import Item
from ..serializers.item import ItemSerializer
from .fixtures.item import ItemTestHarness

ITEM_URL = reverse("v1:items-list")


class PrivateItemTestHarness(ItemTestHarness):

  @classmethod
  def setUpTestData(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']
    cls.store2 = test_data2['store']
    cls.shelf2 = test_data2['shelf']
    super().setUpTestData()

  @classmethod
  def create_data_hook(cls):
    cls.serializer = ItemSerializer
    cls.data1 = {
        'name': "Canned Beans",
        'shelf_life': 99,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3
    }
    cls.data2 = {
        'name': "Lasagna Noodles",
        'shelf_life': 104,
        'user': cls.user1,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store2],
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data = {
        'name': "Microwave Dinner",
        'shelf_life': 109,
        'user': cls.user1.id,
        'shelf': cls.shelf2.id,
        'preferred_stores': [cls.store1.id],
        'price': 2.00,
        'quantity': 3
    }


def item_url_with_params(query_kwargs):
  return '{}?{}'.format(ITEM_URL, urlencode(query_kwargs))


class PublicItemTest(TestCase):
  """Test the public Item API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_login_required(self):
    """Test that login is required for retrieving shelves."""
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


class PrivateItemTest(PrivateItemTestHarness):
  """Test the authorized Item API"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def test_list_items(self):
    """Test retrieving a list of items."""
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL)

    items = Item.objects.all().order_by("index")
    serializer = ItemSerializer(items, many=True)

    assert items.count() == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_retrieve_single_item(self):
    """Test retrieving a single item."""
    item = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL + str(item.id) + "/")

    items = Item.objects.get(id=item.id)
    serializer = ItemSerializer(items)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_list_items_paginated_correctly(self):
    """Test that retrieving a list of items is paginated correctly."""
    for index in range(0, 11):
      data = dict(self.data1)
      data['name'] += str(index)
      self.create_test_instance(**data)

    res = self.client.get(item_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 10)
    self.assertIsNotNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_items_by_store(self):
    """Test retrieving a list of items, filtered by store."""
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"preferred_stores": self.store1.id})
    res = self.client.get(url)

    items = Item.objects.all().order_by("index")
    serializer = ItemSerializer(
        items.filter(preferred_stores__in=[self.store1.id]), many=True
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_items_by_shelf(self):
    """Test retrieving a list of items, filtered by shelf."""
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"shelf": self.shelf1.id})
    res = self.client.get(url)

    items = Item.objects.all().order_by("index")
    serializer = ItemSerializer(items.filter(shelf=self.shelf1.id), many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_delete_item(self):
    """Test deleting a item."""
    delete = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res_delete = self.client.delete(ITEM_URL + str(delete.id) + '/')
    res_get = self.client.get(ITEM_URL)

    items = Item.objects.all().order_by("index")
    serializer = ItemSerializer(items, many=True)

    assert len(items) == 1
    self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(res_get.status_code, status.HTTP_200_OK)
    self.assertEqual(res_get.data['results'], serializer.data)

  def test_create_item(self):
    """Test creating a item."""
    res = self.client.post(ITEM_URL, data=self.serializer_data)

    items = Item.objects.all().order_by("index")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    assert len(items) == 1
    item = items[0]

    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.shelf_life, self.serializer_data['shelf_life'])
    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.shelf.id, self.shelf2.id)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, self.serializer_data['quantity'])

    preferred_stores = item.preferred_stores.all()
    assert len(preferred_stores) == 1
    self.assertEqual(preferred_stores[0].id, self.store1.id)

  def test_update_item(self):
    """Test updating a item."""
    original = self.create_test_instance(**self.data1)
    res = self.client.put(
        ITEM_URL + str(original.id) + '/', data=self.serializer_data
    )

    # Ensure the original object has wrong data
    self.assertNotEqual(original.name, self.serializer_data['name'])

    items = Item.objects.all().order_by("index")
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    assert len(items) == 1
    item = items[0]

    # Check All Fields
    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.shelf_life, self.serializer_data['shelf_life'])
    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.shelf.id, self.shelf2.id)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, self.serializer_data['quantity'])

    preferred_stores = item.preferred_stores.all()
    assert len(preferred_stores) == 1
    self.assertEqual(preferred_stores[0].id, self.store1.id)

    # Update Object and Confirm It is Updated
    original.refresh_from_db()
    self.assertEqual(original.name, self.serializer_data['name'])


class PrivateItemTestAnotherUser(PrivateItemTestHarness):
  """Test the authorized Item API from Another User"""

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  def test_list_items(self):
    """Test retrieving a list of items."""
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_retrieve_single_item(self):
    """Test retrieving a single item."""
    item = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res = self.client.get(ITEM_URL + str(item.id) + "/")
    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_list_items_paginated_correctly(self):
    """Test that retrieving a list of items is paginated correctly."""
    for index in range(0, 11):
      data = dict(self.data1)
      data['name'] += str(index)
      self.create_test_instance(**data)

    res = self.client.get(item_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 0)
    self.assertIsNone(res.data['next'])
    self.assertIsNone(res.data['previous'])

  def test_list_items_by_store(self):
    """Test retrieving a list of items, filtered by store."""
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"preferred_stores": self.store1.id})
    res = self.client.get(url)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_list_items_by_shelf(self):
    """Test retrieving a list of items, filtered by shelf."""
    self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    url = item_url_with_params({"shelf": self.shelf1.id})
    res = self.client.get(url)
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], [])

  def test_delete_item(self):
    """Test deleting a item."""
    delete = self.create_test_instance(**self.data1)
    self.create_test_instance(**self.data2)

    res_delete = self.client.delete(ITEM_URL + str(delete.id) + '/')
    self.assertEqual(res_delete.status_code, status.HTTP_403_FORBIDDEN)

  def test_update_item(self):
    """Test updating a item."""
    original = self.create_test_instance(**self.data1)
    res = self.client.put(
        ITEM_URL + str(original.id) + '/', data=self.serializer_data
    )

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
