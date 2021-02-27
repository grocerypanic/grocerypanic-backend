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
  def setUpTestData(cls):
    super().setUpTestData()
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']
    cls.create_data_hook()

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()

    cls.one_year_ago = cls.today - timedelta(days=365)
    cls.one_year_ago_and_a_day = cls.one_year_ago - timedelta(days=1)
    cls.one_week_ago = cls.today - timedelta(days=14)
    cls.one_month_ago = cls.today - timedelta(days=31)
    cls.timezone_edgecase = cls.today - (
        timedelta(days=cls.item1.shelf_life, hours=10)
    )

  def setUp(self):
    super().setUp()

    self.item2.quantity = 0
    self.item2.save()

    self.purchases1 = self._create_scenarios(30.1, self.item1)
    self.consumptions1 = self._create_scenarios(-1, self.item1)

    self.purchases2 = self._create_scenarios(60.1, self.item2)
    self.consumptions2 = self._create_scenarios(-2, self.item2)

    activities = [
        'p-last_year',
        'c-last_month',
        'p-last_month',
        'p-last_week',
        'c-today',
        'p-today',
    ]

    self._generate_test_data(activities)

  def tearDown(self):
    super().tearDown()
    Inventory.objects.all().delete()

  def assertListAllEqual(self, iterable):
    if len(set(iterable)) > 1:
      raise self.failureException(f"List Contents: {iterable} not all equal.")

  def _generate_test_data(self, activities):
    for activity in activities:
      activity_type, when = activity.split('-')
      if activity_type == 'p':
        self._create_test_transaction(**self.purchases1[when])
        self._create_test_transaction(**self.purchases2[when])
      if activity_type == 'c':
        self._create_test_transaction(**self.consumptions1[when])
        self._create_test_transaction(**self.consumptions2[when])

  def _create_scenarios(self, quantity, item):

    def generate_transaction_data(date_object):
      return {'item': item, 'datetime': date_object, 'quantity': quantity}

    return {
        'today': generate_transaction_data(self.today),
        'last_week': generate_transaction_data(self.one_week_ago),
        'last_month': generate_transaction_data(self.one_month_ago),
        'last_year': generate_transaction_data(self.one_year_ago),
        'timezone_edgecase': generate_transaction_data(self.timezone_edgecase),
    }

  def _create_test_transaction(self, **kwargs):
    transaction = Transaction(**kwargs)
    transaction.save()
    self.objects.append(transaction)
    return transaction

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
    old_inventory_count = Inventory.objects.all().count()

    Inventory.objects.all().delete()
    Transaction.objects.rebuild_inventory_table(confirm=True)

    new_inventory_count = Inventory.objects.all().count()

    self.assertEqual(
        old_inventory_count,
        new_inventory_count,
    )

  def test_rebuild_same_record_quantity(self):
    old_inventory_quantity1 = Inventory.objects.get_quantity(self.item1)
    old_inventory_quantity2 = Inventory.objects.get_quantity(self.item2)

    Inventory.objects.all().delete()
    Transaction.objects.rebuild_inventory_table(confirm=True)

    new_inventory_quantity1 = Inventory.objects.get_quantity(self.item1)
    new_inventory_quantity2 = Inventory.objects.get_quantity(self.item2)

    self._refresh_items()

    self.assertListAllEqual([
        old_inventory_quantity1,
        new_inventory_quantity1,
        self.item1.quantity,
    ])

    self.assertListAllEqual([
        old_inventory_quantity2,
        new_inventory_quantity2,
        self.item2.quantity,
    ])

  def test_rebuild_same_record_expired(self):
    old_inventory_expired1 = Inventory.objects.get_expired(self.item1)
    old_inventory_expired2 = Inventory.objects.get_expired(self.item2)

    Inventory.objects.all().delete()
    Transaction.objects.rebuild_inventory_table(confirm=True)

    new_inventory_expired1 = Inventory.objects.get_expired(self.item1)
    new_inventory_expired2 = Inventory.objects.get_expired(self.item2)

    self._refresh_items()

    self.assertListAllEqual([
        old_inventory_expired1,
        new_inventory_expired1,
        self.item1.expired,
    ])

    self.assertListAllEqual([
        old_inventory_expired2,
        new_inventory_expired2,
        self.item2.expired,
    ])
