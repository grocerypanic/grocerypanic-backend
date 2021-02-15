"""Test the Transaction model."""

from django.core.exceptions import ValidationError
from freezegun import freeze_time

from ...tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..transaction import Transaction
from .fixtures.fixture_models import generate_base


class TestTransaction(generate_base(TransactionTestHarness)):
  """Test the Transaction model."""

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.fields = {}

    def create_transaction_data(quantity):
      return {
          'item': cls.item1,
          'date_object': cls.today,
          'user': cls.user1,
          'quantity': quantity
      }

    cls.positive_data = create_transaction_data(3)
    cls.negative_data = create_transaction_data(-3)
    cls.invalid_data = create_transaction_data(-5)
    cls.zero_data = create_transaction_data(0)

    cls.data = cls.positive_data

  def test_apply_twice(self):

    instance = self.create_test_instance(**self.positive_data)
    self.assertEqual(
        instance.item.quantity,
        self.positive_data['quantity'] + self.initial_quantity
    )
    instance.apply_transaction()
    self.assertEqual(
        instance.item.quantity,
        self.positive_data['quantity'] + self.initial_quantity,
    )

  def test_positive_transaction(self):
    self.create_test_instance(**self.positive_data)

    query = Transaction.objects.filter(item=self.item1)

    assert len(query) == 1
    transaction = query[0]
    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, self.today)
    self.assertEqual(transaction.quantity, self.positive_data['quantity'])
    self.assertEqual(
        transaction.item.quantity,
        self.initial_quantity + self.positive_data['quantity']
    )

  def test_positive_operation(self):
    transaction = self.create_test_instance(**self.positive_data)
    self.assertEqual("Purchase", transaction.operation)

  def test_positive_str(self):
    transaction = self.create_test_instance(**self.positive_data)
    string = "Purchase: %s units of %s" % (
        transaction.quantity, transaction.item.name
    )
    self.assertEqual(string, str(transaction))

  def test_negative_transaction(self):

    self.item1.quantity = 3
    self.item1.save()

    self.create_test_instance(**self.negative_data)
    query = Transaction.objects.filter(item=self.item1)

    assert len(query) == 1
    transaction = query[0]
    self.assertEqual(transaction.item.id, self.item1.id)
    self.assertEqual(transaction.datetime, self.today)
    self.assertEqual(transaction.quantity, self.negative_data['quantity'])
    assert transaction.item.quantity == 3 + self.negative_data['quantity']

  def test_negative_operation(self):

    self.item1.quantity = 3
    self.item1.save()

    transaction = self.create_test_instance(**self.negative_data)
    self.assertEqual("Consumption", transaction.operation)

  def test_negative_str(self):

    self.item1.quantity = 3
    self.item1.save()

    transaction = self.create_test_instance(**self.negative_data)
    string = "Consumption: %s units of %s" % (
        transaction.quantity, transaction.item.name
    )
    self.assertEqual(string, str(transaction))

  def test_zero_transaction(self):
    with self.assertRaises(ValidationError):
      self.create_test_instance(**self.zero_data)

    query = Transaction.objects.filter(item=self.item1)
    assert len(query) == 0
    self.item1.refresh_from_db()
    assert self.item1.quantity == self.initial_quantity

  def test_zero_operation(self):

    self.item1.quantity = 3
    self.item1.save()

    transaction = self.create_test_instance(**self.negative_data)
    transaction.quantity = 0
    self.assertIsNone(transaction.operation)
    transaction.quantity = None
    self.assertIsNone(transaction.operation)

  def test_zero_str(self):

    self.item1.quantity = 3
    self.item1.save()

    transaction = self.create_test_instance(**self.negative_data)
    transaction.quantity = 0
    self.assertEqual("Invalid Transaction", str(transaction))

  def test_invalid_transaction(self):
    with self.assertRaises(ValidationError):
      self.create_test_instance(**self.invalid_data)

    query = Transaction.objects.filter(item=self.item1)
    assert len(query) == 0
    self.item1.refresh_from_db()
    assert self.item1.quantity == self.initial_quantity
