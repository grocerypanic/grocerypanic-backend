"""Test the Item Maintenance manager."""

from datetime import timedelta

from django.utils import timezone
from freezegun import freeze_time

from .....exceptions import ConfirmationRequired
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ....item import Item
from ....transaction import Transaction


@freeze_time("2020-01-14")
class TestMaintenanceManager(TransactionTestHarness):
  """Test the MaintenanceManager model manager class."""

  mute_signals = False

  @classmethod
  def create_data_hook(cls):
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']

    cls.today = timezone.now()

    cls.one_year_ago = cls.today - timedelta(days=365)
    cls.one_year_ago_and_a_day = cls.one_year_ago - timedelta(days=1)
    cls.one_week_ago = cls.today - timedelta(days=14)
    cls.one_month_ago = cls.today - timedelta(days=31)
    cls.timezone_edgecase = cls.today - (
        timedelta(days=cls.item1.shelf_life, hours=10)
    )

    cls.purchases1 = cls._create_scenarios(30.1, cls.item1)
    cls.consumptions1 = cls._create_scenarios(-1, cls.item1)

    cls.purchases2 = cls._create_scenarios(60.1, cls.item2)
    cls.consumptions2 = cls._create_scenarios(-2, cls.item2)

    activities = [
        'p-last_year',
        'c-last_month',
        'p-last_month',
        'p-last_week',
        'c-today',
        'p-today',
    ]

    cls._generate_transactions_from_activities(activities)
    cls._snapshot_item_quantities()

  @classmethod
  def _create_scenarios(cls, quantity, item):

    def generate_transaction_data(date_object):
      return {'item': item, 'datetime': date_object, 'quantity': quantity}

    return {
        'today': generate_transaction_data(cls.today),
        'last_week': generate_transaction_data(cls.one_week_ago),
        'last_month': generate_transaction_data(cls.one_month_ago),
        'last_year': generate_transaction_data(cls.one_year_ago),
        'timezone_edgecase': generate_transaction_data(cls.timezone_edgecase),
    }

  @classmethod
  def _create_test_transaction(cls, **kwargs):
    transaction = Transaction(**kwargs)
    transaction.save()
    return transaction

  @classmethod
  def _generate_transactions_from_activities(cls, activities):
    for activity in activities:
      activity_type, when = activity.split('-')
      if activity_type == 'p':
        cls._create_test_transaction(**cls.purchases1[when])
        cls._create_test_transaction(**cls.purchases2[when])
      if activity_type == 'c':
        cls._create_test_transaction(**cls.consumptions1[when])
        cls._create_test_transaction(**cls.consumptions2[when])

  @classmethod
  def _snapshot_item_quantities(cls):
    cls.original_item1_quantity = cls.item1.quantity
    cls.original_item2_quantity = cls.item2.quantity

  def setUp(self):
    self.objects = list()

  def _refresh_items(self):
    self.item1.invalidate_caches()
    self.item1.refresh_from_db()
    self.item2.invalidate_caches()
    self.item2.refresh_from_db()

  def _set_quantities(self, quantity):
    self.item1.quantity = quantity
    self.item1.save()
    self.item2.quantity = quantity
    self.item2.save()

  def test_rebuild_not_confirmed(self):
    with self.assertRaises(ConfirmationRequired):
      Item.objects.rebuild_quantities_from_inventory()

  def test_rebuild_confirmed(self):
    Item.objects.rebuild_quantities_from_inventory(confirm=True)

  def test_rebuild_same_quantities(self):
    test_quantities = 10
    self._set_quantities(test_quantities)

    Item.objects.rebuild_quantities_from_inventory(confirm=True)
    self._refresh_items()

    self.assertEqual(self.item1.quantity, self.original_item1_quantity)

    self.assertEqual(self.item2.quantity, self.original_item2_quantity)
