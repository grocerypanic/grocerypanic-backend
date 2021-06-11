"""Test the V1 kitchen Item API."""

import faker
from django.urls import reverse
from rest_framework import status

from .bases import APICrudTestHarness, APICrudTestHarnessUnauthorized
from kitchen.models.item import Item


class ItemCrudTest(APICrudTestHarness):
  """Test the V1 Kitchen Item API Authorized endpoints."""

  test_view = 'v1:items-list'
  store_view = 'v1:stores-list'
  shelf_view = 'v1:shelves-list'

  mutable_properties = {
      'has_partial_quantities': True,
      '_index': None,
      'id': False,
      'name': True,
      'shelf': True,
      'shelf_life': True,
      'preferred_stores': True,
      'price': True,
      'quantity': False,
      'user': None,
  }

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.store_view = reverse(cls.store_view)
    cls.shelf_view = reverse(cls.shelf_view)

    cls.test_name = 'test_item_1'
    cls.faker = faker.Faker()

  def setUp(self):
    self._authorize()

  def _assertDatabaseNotMutated(self, pk, object_property, new_value):
    db_object = Item.objects.get(pk=pk)
    self.assertNotEqual(getattr(db_object, object_property), new_value)

  def _check_mutated_data(self, patch_pair, new_item_data, original_data):
    object_property = patch_pair[0]
    requested_value = patch_pair[1]
    pk = new_item_data['id']

    is_mutable = self.mutable_properties[object_property]

    if is_mutable is None:
      self.assertNotIn(object_property, new_item_data.keys())
      self.assertNotIn(object_property, original_data.keys())
      self._assertDatabaseNotMutated(pk, object_property, requested_value)
      return

    original_value = original_data[object_property]
    retrieved_value = new_item_data[object_property]

    has_mutated = original_value != retrieved_value
    self.assertEqual(has_mutated, is_mutable)

  def _create_dependencies(self, index=1):
    shelf_data = {"name": f"test_shelf_{index}"}

    store_data = {"name": f"test_store_{index}"}

    shelf_response = self._api_create(shelf_data, self.shelf_view)
    shelf_id = shelf_response.json()['id']
    self.assertEqual(shelf_response.status_code, status.HTTP_201_CREATED)

    store_response = self._api_create(store_data, self.store_view)
    store_id = store_response.json()['id']
    self.assertEqual(store_response.status_code, status.HTTP_201_CREATED)

    return {"shelf_id": shelf_id, "store_id": store_id}

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

  def _data_generate_item_mutation_data(self):
    alternate_dependencies = self._create_dependencies(index=1)

    item_data = self._data_generate_item_with_dependencies(index=2)
    item_id = item_data['id']

    update_data = {
        '_index': item_data['name'] + self.faker.lexify(text='?'),
        'id': item_id + 1,
        'name': item_data['name'] + self.faker.lexify(text='?'),
        'shelf': alternate_dependencies['store_id'],
        'shelf_life': item_data['shelf_life'] + 1,
        'preferred_stores': [alternate_dependencies['store_id']],
        'price': f"{float(item_data['price']) + 1.0:.2f}",
        'quantity': round(item_data['quantity']) + 1,
        'has_partial_quantities': False,
        'user': self.user.id + 1,
    }

    return update_data, item_data

  def _data_generate_item_with_dependencies(self, index=1):
    dependencies = self._create_dependencies(index)
    item_data = self._data_generate_item(**dependencies)

    item_response = self._api_create(item_data, self.view)
    self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)
    return item_response.json()

  def test_create_list(self):
    dependencies = self._create_dependencies()
    item_data = self._data_generate_item(**dependencies)

    item_response = self._api_create(item_data, self.view)
    self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)

    list_response = self._api_list(self.view)
    self.assertEqual(list_response.status_code, status.HTTP_200_OK)

    created_item = item_response.json()

    self.assertDictEqual(
        list_response.json(),
        {
            'count':
                1,
            'next':
                None,
            'previous':
                None,
            'results': [{
                'id': created_item['id'],
                'has_partial_quantities': True,
                'name': item_data['name'],
                'price': f"{item_data['price']:.2f}",
                'quantity': 0.0,
                'shelf_life': int(item_data['shelf_life']),
                'next_expiry_date': None,
                'next_expiry_datetime': None,
                'next_expiry_quantity': 0.0,
                'expired': 0,
                'shelf': dependencies['shelf_id'],
                'preferred_stores': [dependencies['store_id']],
            },],
        },
    )

  def test_create_detail(self):
    dependencies = self._create_dependencies()
    item_data = self._data_generate_item(**dependencies)

    item_response = self._api_create(item_data, self.view)
    self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)

    detail_response = self._api_detail(
        item_response.json()['id'],
        self.view,
    )
    self.assertEqual(detail_response.status_code, status.HTTP_200_OK)

    self.assertDictEqual(
        detail_response.json(),
        item_response.json(),
    )

  def test_delete_list(self):
    dependencies = self._create_dependencies()
    item_data = self._data_generate_item(**dependencies)

    item_response = self._api_create(item_data, self.view)
    self.assertEqual(item_response.status_code, status.HTTP_201_CREATED)

    delete_response = self._api_delete(item_response.json()['id'], self.view)
    self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    list_response = self._api_list(self.view)
    self.assertEqual(list_response.status_code, status.HTTP_200_OK)

    self.assertDictEqual(
        list_response.json(),
        {
            'count': 0,
            'next': None,
            'previous': None,
            'results': [],
        },
    )

  def test_patch_complies_with_mutable_properties(self):
    update_data, original_item_data = self._data_generate_item_mutation_data()
    item_pk = original_item_data['id']

    for update_pair in update_data.items():
      patch_data_pair = {update_pair[0]: update_pair[1]}
      with self.subTest(patch_data_pair=patch_data_pair):

        new_item_data = self._api_patch(
            item_pk,
            patch_data_pair,
            self.view,
        )

        self.assertEqual(new_item_data.status_code, status.HTTP_200_OK)
        self._check_mutated_data(
            update_pair,
            new_item_data.json(),
            original_item_data,
        )

  def test_put_complies_with_mutable_properties(self):
    put_data, original_item_data = self._data_generate_item_mutation_data()
    item_pk = original_item_data['id']

    put_response = self._api_put(
        item_pk,
        put_data,
        self.view,
    )

    self.assertEqual(put_response.status_code, status.HTTP_200_OK)

    for update_pair in put_data.items():
      put_data_pair = {update_pair[0]: update_pair[1]}
      with self.subTest(put_data_pair=put_data_pair):

        self._check_mutated_data(
            update_pair,
            put_response.json(),
            original_item_data,
        )


class ItemCrudTestUnauthorized(APICrudTestHarnessUnauthorized):
  """Test the V1 Kitchen Item API Authorized endpoints anonymously."""

  test_view = 'v1:items-list'
  __test__ = True
