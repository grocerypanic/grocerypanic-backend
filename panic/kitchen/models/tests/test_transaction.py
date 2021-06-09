"""Test the Transaction model."""

from django.core.exceptions import ValidationError
from freezegun import freeze_time

from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_transaction import TransactionTestHarness
from ..transaction import Transaction


class TestTransaction(ModelTestMixin, TransactionTestHarness):
  """Test the Transaction model."""

  mute_signals = False

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    cls.fields = {}

    def create_transaction_data(quantity):
      return {'item': cls.item1, 'date_object': cls.today, 'quantity': quantity}

    cls.positive_data = create_transaction_data(3)
    cls.negative_data = create_transaction_data(-3)
    cls.invalid_data = create_transaction_data(-5)
    cls.zero_data = create_transaction_data(0)

    cls.create_data = cls.positive_data

  def test_positive_transaction(self):
    transaction = self.create_test_instance(**self.positive_data)

    query = Transaction.objects.filter(item=self.item1)

    self.assertQuerysetEqual(query, [transaction])

    self.assertEqual(
        transaction.item.quantity,
        self.initial_quantity + self.positive_data['quantity'],
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
    initial = self.create_test_instance(**self.positive_data)
    transaction = self.create_test_instance(**self.negative_data)
    query = Transaction.objects.filter(item=self.item1)

    self.assertQuerysetEqual(
        query,
        [initial, transaction],
        ordered=False,
    )
    self.assertEqual(
        transaction.item.quantity,
        initial.quantity + self.negative_data['quantity'],
    )

  def test_negative_operation(self):
    self.create_test_instance(**self.positive_data)

    transaction = self.create_test_instance(**self.negative_data)
    self.assertEqual("Consumption", transaction.operation)

  def test_negative_str(self):
    self.create_test_instance(**self.positive_data)

    transaction = self.create_test_instance(**self.negative_data)
    string = "Consumption: %s units of %s" % (
        transaction.quantity, transaction.item.name
    )
    self.assertEqual(string, str(transaction))

  def test_zero_transaction(self):
    with self.assertRaises(ValidationError):
      self.create_test_instance(**self.zero_data)

    query = Transaction.objects.filter(item=self.item1)
    self.assertEqual(len(query), 0)
    self.item1.refresh_from_db()
    self.assertEqual(self.item1.quantity, self.initial_quantity)

  def test_zero_operation(self):
    self.create_test_instance(**self.positive_data)

    transaction = self.create_test_instance(**self.negative_data)
    transaction.quantity = 0
    self.assertIsNone(transaction.operation)
    transaction.quantity = None
    self.assertIsNone(transaction.operation)

  def test_zero_str(self):
    self.create_test_instance(**self.positive_data)

    transaction = self.create_test_instance(**self.negative_data)
    transaction.quantity = 0
    self.assertEqual("Invalid Transaction", str(transaction))

  def test_invalid_transaction(self):
    with self.assertRaises(ValidationError):
      self.create_test_instance(**self.invalid_data)

    query = Transaction.objects.filter(item=self.item1)
    self.assertEqual(len(query), 0)
    self.item1.refresh_from_db()
    self.assertEqual(self.item1.quantity, self.initial_quantity)

  def test_apply_transaction_on_create_wo_force(self):
    model_data = {
        'item': self.item1,
        'datetime': self.today,
        'quantity': 3,
    }

    transaction = Transaction(**model_data)
    transaction.apply_transaction_to_item()

    self.assertEqual(
        transaction.item.quantity,
        transaction.quantity,
    )

  def test_apply_transaction_on_create_w_force(self):
    model_data = {
        'item': self.item1,
        'datetime': self.today,
        'quantity': 3,
    }

    transaction = Transaction(**model_data)
    transaction.apply_transaction_to_item(force=True)

    self.assertEqual(
        transaction.item.quantity,
        transaction.quantity,
    )

  def test_apply_transaction_on_update_wo_force(self):
    transaction = self.create_test_instance(**self.positive_data)
    transaction.apply_transaction_to_item()

    self.assertEqual(
        transaction.item.quantity,
        transaction.quantity,
    )

  def test_apply_transaction_on_update_w_force(self):
    transaction = self.create_test_instance(**self.positive_data)
    transaction.apply_transaction_to_item(force=True)

    self.assertEqual(
        transaction.item.quantity,
        transaction.quantity * 2,
    )
