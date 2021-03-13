"""Test harness for the ItemActivityReport API ViewSet."""

from django.utils import timezone

from ....tests.fixtures.fixtures_django import MockRequest, deserialize_date
from ....tests.fixtures.fixtures_transaction import TransactionTestHarness


class ItemActivityViewSetHarness(TransactionTestHarness):
  """Test harness for the ItemActivityReport API ViewSet."""

  mute_signals = False
  transaction_data: list

  @classmethod
  def create_data_hook(cls):
    cls.serializer_data = {'item': cls.item1.id, 'quantity': 3}

    cls.timezone = "Pacific/Honolulu"
    cls.today = timezone.now()

    cls.initial_transaction_date = cls.today - timezone.timedelta(days=365)
    cls.five_days_ago = cls.today - timezone.timedelta(days=5)
    cls.sixteen_days_ago = cls.today - timezone.timedelta(days=16)

    cls.transaction_data = [
        {
            'date_object': cls.initial_transaction_date,
            'quantity': 200
        },
        {
            'date_object': cls.sixteen_days_ago,
            'quantity': -5
        },
        {
            'date_object': cls.five_days_ago,
            'quantity': -5
        },
        {
            'date_object': cls.today,
            'quantity': -5
        },
    ]

    cls.transaction_16_days_ago = cls._generate_transaction_data()
    cls.transaction_5_days_ago = cls._generate_transaction_data()
    cls.transaction_today = cls._generate_transaction_data()
    cls.initial_transaction = cls._generate_transaction_data()

    cls.MockRequest = MockRequest(cls.user1)

  @classmethod
  def _generate_transaction_data(cls):
    base = {
        'user': cls.user1,
        'item': cls.item1,
    }
    base.update(cls.transaction_data.pop())
    return base

  def setUp(self):
    super().setUp()
    self.reset_item1()
    self.populate_history()

  @staticmethod
  def deserialize_date(string):
    return deserialize_date(string)

  def populate_history(self):
    self.create_test_instance(**self.initial_transaction)
    self.create_test_instance(**self.transaction_16_days_ago)
    self.create_test_instance(**self.transaction_5_days_ago)
    self.create_test_instance(**self.transaction_today)
