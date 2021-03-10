"""Test the Transaction serializer."""

from django.utils import timezone
from freezegun import freeze_time
from rest_framework.serializers import ErrorDetail, ValidationError

from ...exceptions import ValidationPermissionError
from ...models.item import Item
from ...models.transaction import Transaction
from ...tests.fixtures.fixture_mixins import SerializerTestMixin
from ...tests.fixtures.fixtures_django import MockRequest, deserialize_datetime
from ...tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..transaction import TransactionSerializer


class TestTransactionSerializer(SerializerTestMixin, TransactionTestHarness):
  """Test the Transaction serializer."""

  item2: Item
  serializer_data: dict
  fields: dict

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer = TransactionSerializer
    cls.fields = {"name": 255}
    cls.request = MockRequest(cls.user1)

    cls.calculated_properties = set()
    cls.m2m_fields = set()

    cls.today = timezone.now()

    cls.create_data = {
        'item': cls.item1,
        'date_object': cls.today,
        'quantity': 3
    }

    cls.serializer_data = {
        'item': cls.item1.id,
        'datetime': cls.today,
        'quantity': 3
    }

    cls.serializer_data_wrong_item = dict(cls.serializer_data)
    cls.serializer_data_wrong_item.update({
        'item': cls.item2.id,
    })

  @classmethod
  def setUpTestData(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']
    cls.store2 = test_data2['store']
    cls.shelf2 = test_data2['shelf']
    cls.item2 = test_data2['item']
    super().setUpTestData()

  def test_deserialize(self):
    transaction = self.create_test_instance(**self.create_data)
    serialized = self.serializer(transaction)
    deserialized = serialized.data

    representation = self._instance_to_dict(transaction)

    deserialized['datetime'] = \
        deserialize_datetime(deserialized['datetime'])

    self.assertDictEqual(representation, deserialized)

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Transaction.objects.filter(item=self.serializer_data['item'])

    assert len(query) == 1
    transaction = query[0]

    expected = dict(self.serializer_data)
    representation = self._instance_to_dict_subset(transaction, expected)

    self.assertDictEqual(representation, expected)

  def test_serializer_user(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Transaction.objects.filter(item=self.serializer_data['item'])

    assert len(query) == 1
    transaction = query[0]

    self.assertEqual(transaction.item.user.id, self.user1.id)

  def test_serialize_wrong_item(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data_wrong_item,
    )

    with self.assertRaises(ValidationError) as raised:
      serialized.is_valid(raise_exception=True)

    self.assertEqual(
        raised.exception.detail,
        {
            'item': [
                ErrorDetail(
                    string="Please provide a valid item.",
                    code=ValidationPermissionError.default_code
                ),
            ],
        },
    )
