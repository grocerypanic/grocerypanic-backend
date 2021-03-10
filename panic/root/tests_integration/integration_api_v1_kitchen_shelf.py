"""Test the V1 kitchen Shelf API."""

from rest_framework import status

from .bases import APICrudTestHarness, APICrudTestHarnessUnauthorized


class ShelfCrudTest(APICrudTestHarness):
  """Test the V1 Kitchen Shelf API Auth endpoints with user data."""

  test_view = 'v1:shelves-list'

  def setUp(self):
    self.test_name = 'test_shelf_1'
    self.test_data = {'name': self.test_name}
    self._authorize()

  def test_create(self):
    create_response = self._api_create(self.test_data, self.view)
    self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

    list_response = self._api_list(self.view)
    self.assertEqual(list_response.status_code, status.HTTP_200_OK)

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
                'id': create_response.json()['id'],
                'name': self.test_name,
            },],
        },
    )

  def test_delete(self):
    response = self._api_create(self.test_data, self.view)
    self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    response = self._api_delete(response.json()['id'], self.view)
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    response = self._api_list(self.view)
    self.assertEqual(response.status_code, status.HTTP_200_OK)

    self.assertDictEqual(
        response.json(),
        {
            'count': 0,
            'next': None,
            'previous': None,
            'results': [],
        },
    )

  def test_patch(self):
    response = self._api_patch(1, self.test_data, self.view)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_put(self):
    response = self._api_put(1, self.test_data, self.view)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

  def test_detail(self):
    response = self._api_detail(1, self.view)
    self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ShelfCrudTestUnauthorized(APICrudTestHarnessUnauthorized):
  """Test the V1 Kitchen Shelf API Authorized endpoints anonymously."""

  test_view = 'v1:shelves-list'
  __test__ = True
