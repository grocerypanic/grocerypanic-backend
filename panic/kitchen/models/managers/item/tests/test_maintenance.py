"""Test the Item Maintenance manager."""

from datetime import timedelta

from django.utils import timezone
from freezegun import freeze_time

from .....exceptions import ConfirmationRequired
from .....tests.fixtures.fixtures_transaction import TransactionTestHarness
from ....inventory import Inventory
from ....item import Item
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
    item1_original_quantity = self.item1.quantity
    item2_original_quantity = self.item2.quantity

    test_quantities = 10
    self._set_quantities(test_quantities)

    Item.objects.rebuild_quantities_from_inventory(confirm=True)
    self._refresh_items()

    self.assertEqual(self.item1.quantity, item1_original_quantity)

    self.assertEqual(self.item2.quantity, item2_original_quantity)
