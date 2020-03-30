"""Test the Item API."""

from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models.item import Item
from ..models.shelf import Shelf
from ..models.store import Store
from ..serializers.item import ItemSerializer

ITEM_URL = reverse("kitchen:item-list")


class PublicItemTest(TestCase):
  """Test the public Item API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_login_required(self):
    """Test that login is required for retrieving shelves."""
    res = self.client.get(ITEM_URL)

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_create_login_required(self):
    payload = {}
    res = self.client.post(ITEM_URL, data=payload)

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

  def test_update_login_required(self):
    payload = {}
    res = self.client.put(ITEM_URL, data=payload)

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateItemTest(TestCase):
  """Test the authorized Item API"""

  # pylint: disable=R0913
  def sample_item(self, user, name, bestbefore, shelf, preferred_stores, price,
                  quantity):
    """Create a test item."""
    if user is None:
      user = self.user
    item = Item.objects.create(name=name,
                               user=user,
                               bestbefore=bestbefore,
                               shelf=shelf,
                               price=price,
                               quantity=quantity)
    item.preferred_stores.add(preferred_stores)
    item.save()
    self.objects.append(item)
    return item

  @classmethod
  def setUpTestData(cls):
    cls.serializer = ItemSerializer
    cls.today = date.today()
    cls.fields = {"name": 255}
    cls.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )
    cls.store = Store.objects.create(
        user=cls.user,
        name="No Frills",
    )
    cls.shelf = Shelf.objects.create(
        user=cls.user,
        name="Pantry",
    )
    cls.fridge = Shelf.objects.create(
        user=cls.user,
        name="Refrigerator",
    )
    cls.data1 = {
        'name': "Canned Beans",
        'bestbefore': cls.today,
        'user': cls.user,
        'shelf': cls.shelf,
        'preferred_stores': cls.store,
        'price': 2.00,
        'quantity': 3
    }
    cls.data2 = {
        'name': "Lasagna Noodles",
        'bestbefore': cls.today,
        'user': cls.user,
        'shelf': cls.shelf,
        'preferred_stores': cls.store,
        'price': 2.00,
        'quantity': 3
    }
    cls.serializer_data = {
        'name': "Microwave Dinner",
        'bestbefore': cls.today,
        'user': cls.user.id,
        'shelf': cls.fridge.id,
        'preferred_stores': [cls.store.id],
        'price': 2.00,
        'quantity': 3
    }

  def setUp(self):
    self.objects = list()
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()

  def test_retrieve_items(self):
    """Test retrieving a list of items."""
    self.sample_item(**self.data1)
    self.sample_item(**self.data2)

    res = self.client.get(ITEM_URL)

    items = Item.objects.all().order_by("-name")
    serializer = ItemSerializer(items, many=True)

    assert len(items) == 2
    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data, serializer.data)

  def test_delete_item(self):
    """Test deleting a item."""
    delete = self.sample_item(**self.data1)
    self.sample_item(**self.data2)

    res_delete = self.client.delete(ITEM_URL + str(delete.id) + '/')
    res_get = self.client.get(ITEM_URL)

    items = Item.objects.all().order_by("-name")
    serializer = ItemSerializer(items, many=True)

    assert len(items) == 1
    self.assertEqual(res_delete.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(res_get.status_code, status.HTTP_200_OK)
    self.assertEqual(res_get.data, serializer.data)

  def test_create_item(self):
    """Test creating a item."""
    res = self.client.post(ITEM_URL, data=self.serializer_data)

    items = Item.objects.all().order_by("-name")
    self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    assert len(items) == 1
    item = items[0]

    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.bestbefore, self.today)
    self.assertEqual(item.user.id, self.user.id)
    self.assertEqual(item.shelf.id, self.fridge.id)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, self.serializer_data['quantity'])

    preferred_stores = item.preferred_stores.all()
    assert len(preferred_stores) == 1
    self.assertEqual(preferred_stores[0].id, self.store.id)

  def test_update_item(self):
    """Test updating a item."""
    original = self.sample_item(**self.data1)
    res = self.client.put(ITEM_URL + str(original.id) + '/',
                          data=self.serializer_data)

    # Ensure the original object has wrong data
    self.assertNotEqual(original.name, self.serializer_data['name'])

    items = Item.objects.all().order_by("-name")
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    assert len(items) == 1
    item = items[0]

    # Check All Fields
    self.assertEqual(item.name, self.serializer_data['name'])
    self.assertEqual(item.bestbefore, self.today)
    self.assertEqual(item.user.id, self.user.id)
    self.assertEqual(item.shelf.id, self.fridge.id)
    self.assertEqual(item.price, self.serializer_data['price'])
    self.assertEqual(item.quantity, self.serializer_data['quantity'])

    preferred_stores = item.preferred_stores.all()
    assert len(preferred_stores) == 1
    self.assertEqual(preferred_stores[0].id, self.store.id)

    # Update Object and Confirm It is Updated
    original.refresh_from_db()
    self.assertEqual(original.name, self.serializer_data['name'])
