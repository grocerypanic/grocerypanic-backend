"""Test the Item Quantity manager."""

from datetime import timedelta

from django.utils import timezone
from freezegun import freeze_time

from .....tests.fixtures.fixtures_item import ItemTestHarness
from ....inventory import Inventory
from ....transaction import Transaction


@freeze_time("2020-01-14")
class TestQuantityManager(ItemTestHarness):
  """Test the QuantityManager model manager class."""

  mute_signals = False

  def setUp(self):
    super().setUp()
    self.user1.timezone = "Pacific/Honolulu"
    self.user1.save()

  def tearDown(self):
    Inventory.objects.all().delete()

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.fields = {"name": 255}
    cls.data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 300,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
        'quantity': 3,
    }
    cls.zeroed_data = dict(cls.data)
    cls.zeroed_data.update({"quantity": 0})

    cls.user1.timezone = "Pacific/Honolulu"
    cls.user1.save()

    cls.one_year_ago = cls.today - timedelta(days=365)
    cls.one_year_ago_and_a_day = cls.one_year_ago - timedelta(days=1)
    cls.one_week_ago = cls.today - timedelta(days=14)
    cls.one_month_ago = cls.today - timedelta(days=31)

    cls.item = cls.create_instance(**cls.zeroed_data)

  def _create_scenarios(self, quantity):

    item = self.item

    def generate_transaction_data(date_object):
      return {'item': item, 'datetime': date_object, 'quantity': quantity}

    return {
        'today':
            generate_transaction_data(self.today),
        'last_week':
            generate_transaction_data(self.one_week_ago),
        'last_month':
            generate_transaction_data(self.one_month_ago),
        'last_year_and_a_day':
            generate_transaction_data(self.one_year_ago_and_a_day),
        'last_year':
            generate_transaction_data(self.one_year_ago),
    }

  def _create_test_transaction(self, **kwargs):
    transaction = Transaction(**kwargs)
    transaction.save()
    self.objects.append(transaction)
    return transaction

  def test_get_quantity(self):
    quantity = 30.1
    scenarios = self._create_scenarios(quantity)

    self._create_test_transaction(**scenarios['today'])
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])
    self._create_test_transaction(**scenarios['last_year'])

    received_quantity = Inventory.objects.get_quantity(self.item)

    self.assertEqual(
        received_quantity,
        quantity * 4,
    )

  def test_get_quantity_partial_usage(self):
    quantity = 30.1
    usage_quantity = -1.0

    scenarios = self._create_scenarios(quantity)
    usage_scenarios = self._create_scenarios(usage_quantity)

    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**usage_scenarios['today'])

    received_quantity = Inventory.objects.get_quantity(self.item)

    self.assertEqual(
        received_quantity,
        quantity + usage_quantity,
    )

  def test_get_quantity_none(self):
    received_quantity = Inventory.objects.get_quantity(self.item)

    self.assertEqual(
        received_quantity,
        0,
    )
