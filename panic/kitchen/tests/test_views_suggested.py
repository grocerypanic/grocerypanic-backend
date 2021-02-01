"""Test the list items API."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.test import APIClient

from ..models.suggested import SuggestedItem
from ..serializers.suggested import SuggestedItemSerializer

LIST_URL = reverse("v1:suggestions-list")


def item_url_with_params(query_kwargs):
  return '{}?{}'.format(LIST_URL, urlencode(query_kwargs))


class PublicListItemsTest(TestCase):
  """Test the public Suggested Items API"""

  def setUp(self) -> None:
    self.client = APIClient()

  def test_login_required(self):
    """Test that login is required for retrieving items."""
    res = self.client.get(LIST_URL)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

  def test_create_item_login_required(self):
    payload = {"name": "Meat"}
    res = self.client.post(LIST_URL, payload)

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateListItemsTest(TestCase):
  """Test the authorized Suggested Items API"""

  def create_item(self, name):
    item = SuggestedItem.objects.create(name=name)
    self.objects.append(item)
    return item

  @classmethod
  def setUpTestData(cls):
    cls.objects = list()
    cls.user = get_user_model().objects.create_user(
        username="testuser",
        email="test@niallbyrne.ca",
        password="test123",
    )
    cls.serializer = SuggestedItemSerializer
    cls.fields = {"name": 255}

  def setUp(self):
    self.objects = list()
    self.client = APIClient()
    self.client.force_authenticate(self.user)

  def tearDown(self) -> None:
    for obj in self.objects:
      obj.delete()

  def test_list_items(self):
    """Test retrieving item names."""
    self.create_item(name="Red Bean Dessert")
    self.create_item(name="Tofu")

    res = self.client.get(LIST_URL)

    items = SuggestedItem.objects.all().order_by("name")
    serializer = self.serializer(items, many=True)

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['results'], serializer.data)

  def test_list_items_paginated_correctly(self):
    """Test that retrieving a list of item names is paginated correctly."""
    for index in range(0, 11):
      data = "name" + str(index)
      self.create_item(name=data)

    res = self.client.get(item_url_with_params({"page_size": 10}))
    self.assertEqual(len(res.data['results']), 10)
    self.assertIsNotNone(res.data['next'])
    self.assertIsNone(res.data['previous'])
