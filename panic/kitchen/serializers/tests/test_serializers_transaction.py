"""Test the Transaction serializer."""

from django.utils import timezone
from freezegun import freeze_time
from rest_framework.serializers import ErrorDetail, ValidationError

from ...exceptions import ValidationPermissionError
from ...models.transaction import Transaction
from ...tests.fixtures.fixtures_django import MockRequest, deserialize_datetime
from ...tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..transaction import TransactionSerializer
from .fixtures.fixtures_serializers import generate_base


class TestTransactionSerializer(generate_base(TransactionTestHarness)):
  """Test the Transaction serializer."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer = TransactionSerializer
    cls.today = timezone.now()
    cls.fields = {"name": 255}

    cls.data = {'item': cls.item1, 'date_object': cls.today, 'quantity': 3}
    cls.serializer_data = {
        'item': cls.item1.id,
        'datetime': cls.today,
        'quantity': 3
    }
    cls.serializer_data_wrong_item = {
        'item': cls.item2.id,
        'datetime': cls.today,
        'quantity': 3
    }
    cls.request = MockRequest(cls.user1)

  @classmethod
  def setUpTestData(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']
    cls.store2 = test_data2['store']
    cls.shelf2 = test_data2['shelf']
    cls.item2 = test_data2['item']
    super().setUpTestData()

  def setUp(self):
    self.objects = list()
    self.item1.quantity = 3
    self.item1.save()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def test_deserialize(self):
    transaction = self.create_test_instance(**self.data)
    serialized = self.serializer(transaction)
    deserialized = serialized.data

    self.assertEqual(deserialize_datetime(deserialized['datetime']), self.today)
    self.assertEqual(deserialized['item'], self.item1.id)
    self.assertEqual(deserialized['quantity'], self.data['quantity'])

  def test_serialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Transaction.objects.filter(item__user=self.user1.id)

    assert len(query) == 1
    transaction = query[0]

    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, self.today)
    self.assertEqual(transaction.quantity, self.serializer_data['quantity'])

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
