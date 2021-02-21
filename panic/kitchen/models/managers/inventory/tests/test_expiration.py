"""Test the Item Expiration manager."""

from datetime import timedelta

import pendulum
from django.utils import timezone
from freezegun import freeze_time

from .....tests.fixtures.fixtures_item import ItemTestHarness
from ....inventory import Inventory
from ....transaction import Transaction


@freeze_time("2020-01-14")
class TestExpirationManager(ItemTestHarness):
  """Test the ExpirationManager model manager class."""

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
    }
    cls.user1.timezone = "Pacific/Honolulu"
    cls.user1.save()

    cls.one_year_ago = cls.today - timedelta(days=365)
    cls.one_year_ago_and_a_day = cls.one_year_ago - timedelta(days=1)
    cls.one_week_ago = cls.today - timedelta(days=14)
    cls.one_month_ago = cls.today - timedelta(days=31)

    cls.item = cls.create_instance(**cls.data)

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

  @staticmethod
  def _user_time(user, datetime_object):
    return datetime_object.astimezone(user.timezone).date()

  def _user_expiry_date(self, item, datetime_object):
    expiry_date = datetime_object + timedelta(days=item.shelf_life)
    return self._user_time(item.user, expiry_date)

  def _create_test_transaction(self, **kwargs):
    transaction = Transaction(**kwargs)
    transaction.save()
    self.objects.append(transaction)
    return transaction

  def test_get_next_expiry_date(self):
    scenarios = self._create_scenarios(30.1)
    self._create_test_transaction(**scenarios['today'])
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['last_year'])

    expected_date = self._user_expiry_date(self.item, self.one_month_ago)
    received_date = Inventory.objects.get_next_expiry_date(self.item)

    self.assertEqual(
        expected_date,
        received_date,
    )

  def test_get_next_expiry_date_no_unexpired_items(self):
    scenarios = self._create_scenarios(20.1)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])

    expected_date = None
    received_date = Inventory.objects.get_next_expiry_date(self.item)

    self.assertEqual(
        expected_date,
        received_date,
    )

  def test_get_next_expiry_date_tz_diff(self):
    scenarios = self._create_scenarios(10.1)
    self._create_test_transaction(**scenarios['today'])

    timezone1 = "Pacific/Honolulu"
    timezone2 = "Asia/Hong_Kong"

    self.item.user.timezone = timezone2
    self.item.user.save()

    tz2_date = Inventory.objects.get_next_expiry_date(self.item)

    self.item.user.timezone = timezone1
    self.item.user.save()

    tz1_date = Inventory.objects.get_next_expiry_date(self.item)

    self.assertNotEqual(tz1_date, tz2_date)

  def test_get_next_expired_quantity(self):
    quantity = 30.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['last_month'])
    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity * 2)

  def test_get_next_expired_quantity_with_usage(self):
    quantity = 30.1
    usage_quantity = -1

    scenarios = self._create_scenarios(quantity)
    usage_scenarios = self._create_scenarios(usage_quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**usage_scenarios['today'])
    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity + usage_quantity)

  def test_get_next_expired_quantity_multiple_dates(self):
    quantity = 20.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity)

  def test_get_next_expired_quantity_no_unexpired_items(self):
    quantity = 10.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])

    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, 0)

  def test_get_expired(self):
    quantity = 30.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, quantity * 2)

  def test_get_expired_with_usage(self):
    quantity = 30.1
    usage_quantity = -1

    scenarios = self._create_scenarios(quantity)
    usage_scenarios = self._create_scenarios(usage_quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])
    self._create_test_transaction(**usage_scenarios['today'])

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, quantity * 2 + usage_quantity)

  def test_get_expired_no_expired_items(self):
    quantity = 20.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, 0)

  def test_get_inventory_expiration_datetime(self):
    expected_date = (
        pendulum.now(tz=self.item.user.timezone) -
        timedelta(days=self.item.shelf_life)
    ).start_of('day')

    received_data = Inventory.objects.get_inventory_expiration_datetime(
        self.item
    )

    self.assertEqual(received_data, expected_date)

  def test_get_inventory_expiration_datetime_tz_diff(self):
    timezone1 = "Pacific/Honolulu"
    timezone2 = "Asia/Hong_Kong"

    self.item.user.timezone = timezone2
    self.item.user.save()

    tz2_date = Inventory.objects.get_inventory_expiration_datetime(self.item)

    self.item.user.timezone = timezone1
    self.item.user.save()

    tz1_date = Inventory.objects.get_inventory_expiration_datetime(self.item)

    self.assertNotEqual(tz1_date, tz2_date)
