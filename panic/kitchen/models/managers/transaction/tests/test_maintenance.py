"""Test the Transaction Maintenance manager."""

from datetime import timedelta

from django.utils import timezone
from freezegun import freeze_time

from .....exceptions import ConfirmationRequired
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ....inventory import Inventory
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
    cls._snapshot_inventory_table()

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
  def _snapshot_inventory_table(cls):
    cls.original_inventory_count = Inventory.objects.all().count()
    cls.original_item1_quantity = Inventory.objects.get_quantity(cls.item1)
    cls.original_item2_quantity = Inventory.objects.get_quantity(cls.item2)
    cls.original_item1_expired = Inventory.objects.get_expired(cls.item1)
    cls.original_item2_expired = Inventory.objects.get_expired(cls.item2)

  def assertListAllEqual(self, iterable):
    if len(set(iterable)) > 1:
      raise self.failureException(f"List Contents: {iterable} not all equal.")

  def _refresh_items(self):
    self.item1.invalidate_caches()
    self.item1.refresh_from_db()
    self.item2.invalidate_caches()
    self.item2.refresh_from_db()

  def test_rebuild_not_confirmed(self):
    with self.assertRaises(ConfirmationRequired):
      Transaction.objects.rebuild_inventory_table()

  def test_rebuild_confirmed(self):
    Transaction.objects.rebuild_inventory_table(confirm=True)

  def test_rebuild_same_record_count(self):
    Transaction.objects.rebuild_inventory_table(confirm=True)
    new_inventory_count = Inventory.objects.all().count()

    self.assertEqual(
        self.original_inventory_count,
        new_inventory_count,
    )

  def test_rebuild_same_record_quantity(self):
    Transaction.objects.rebuild_inventory_table(confirm=True)
    new_inventory_quantity1 = Inventory.objects.get_quantity(self.item1)
    new_inventory_quantity2 = Inventory.objects.get_quantity(self.item2)

    self._refresh_items()

    self.assertEqual(
        self.original_item1_quantity,
        new_inventory_quantity1,
    )

    self.assertEqual(
        self.original_item2_quantity,
        new_inventory_quantity2,
    )

  def test_rebuild_same_record_expired(self):
    Transaction.objects.rebuild_inventory_table(confirm=True)
    new_inventory_expired1 = Inventory.objects.get_expired(self.item1)
    new_inventory_expired2 = Inventory.objects.get_expired(self.item2)

    self._refresh_items()

    self.assertListAllEqual([
        self.original_item1_expired,
        new_inventory_expired1,
        self.item1.expired,
    ])

    self.assertListAllEqual([
        self.original_item2_expired,
        new_inventory_expired2,
        self.item2.expired,
    ])
