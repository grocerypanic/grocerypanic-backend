"""Test the Transaction Serializer."""

from django.utils import timezone
from freezegun import freeze_time
from rest_framework.serializers import ValidationError

from ..models.transaction import Transaction
from ..serializers.transaction import TransactionSerializer
from .fixtures.django import MockRequest, deserialize_datetime
from .fixtures.transaction import TransactionTestHarness


class TestTransactionSerializer(TransactionTestHarness):

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.serializer = TransactionSerializer
    cls.today = timezone.now()
    cls.fields = {"name": 255}

    cls.data = {
        'item': cls.item1,
        'date_object': cls.today,
        'user': cls.user1,
        'quantity': 3
    }
    cls.serializer_data = {
        'item': cls.item1.id,
        'datetime': cls.today,
        'quantity': 3
    }
    cls.request = MockRequest(cls.user1)

  @staticmethod
  def generate_overload(fields):
    return_list = []
    for key, value in fields.items():
      overloaded = dict()
      overloaded[key] = "abc" * value
      return_list.append(overloaded)
    return return_list

  def setUp(self):
    self.objects = list()
    self.item1.quantity = 3
    self.item1.save()

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def testDeserialize(self):
    transaction = self.create_test_instance(**self.data)
    serialized = self.serializer(transaction)
    deserialized = serialized.data

    self.assertEqual(deserialize_datetime(deserialized['datetime']), self.today)
    self.assertEqual(deserialized['item'], self.item1.id)
    self.assertEqual(deserialized['quantity'], self.data['quantity'])
    assert 'user' not in deserialized

  def testSerialize(self):
    serialized = self.serializer(
        context={'request': self.request},
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)
    serialized.save()

    query = Transaction.objects.filter(user=self.user1.id)

    assert len(query) == 1
    transaction = query[0]

    self.assertEqual(transaction.user.id, self.user1.id)
    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, self.today)
    self.assertEqual(transaction.quantity, self.serializer_data['quantity'])

  def testFieldLengths(self):
    overloads = self.generate_overload(self.fields)
    for overload in overloads:
      local_data = dict(self.data)
      local_data.update(overload)
      with self.assertRaises(ValidationError):
        serialized = self.serializer(
            context={'request': self.request},
            data=local_data,
        )
        serialized.is_valid(raise_exception=True)
