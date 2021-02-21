"""Test the Item Expiration manager."""

from datetime import timedelta

import pendulum
import pytz
from django.utils import timezone
from freezegun import freeze_time

from .....tests.fixtures.fixtures_item import ItemTestHarness
from ....inventory import Inventory
from ....transaction import Transaction


@freeze_time("2020-01-14")
class ExpirationManagerTestHarness(ItemTestHarness):
  """Test harness for the ExpirationManager model manager class."""

  mute_signals = False

  def setUp(self):
    super().setUp()
    self.user1.timezone = "UTC"
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
    cls.timezone_edgecase = cls.today - (
        timedelta(days=cls.data['shelf_life'], hours=10)
    )

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
        'timezone_edgecase':
            generate_transaction_data(self.timezone_edgecase),
    }

  def _user_expiry_datetime(self, item, datetime_object):
    expiry_datetime = datetime_object + timedelta(days=item.shelf_life)
    return self._user_time(item.user, expiry_datetime)

  @staticmethod
  def _user_time(user, datetime_object):
    return datetime_object.astimezone(user.timezone).date()

  @staticmethod
  def _user_tzinfo(user):
    return pendulum.instance(timezone.now().astimezone(user.timezone)).tzinfo

  def _create_test_transaction(self, **kwargs):
    transaction = Transaction(**kwargs)
    transaction.save()
    self.objects.append(transaction)
    return transaction


class TestGetExpired(ExpirationManagerTestHarness):
  """Test the `ExpirationManager.get_expired` method."""

  def test_utc(self):
    quantity = 30.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])
    self._create_test_transaction(**scenarios['timezone_edgecase'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, quantity * 3)

  def test_honolulu(self):
    quantity = 30.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])
    self._create_test_transaction(**scenarios['timezone_edgecase'])

    self.item.user.timezone = "Pacific/Honolulu"
    self.item.user.save()

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, quantity * 2)

  def test_tz_diff(self):
    scenarios = self._create_scenarios(10.1)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])
    self._create_test_transaction(**scenarios['timezone_edgecase'])

    timezone1 = "UTC"
    timezone2 = "Pacific/Honolulu"

    self.item.user.timezone = timezone1
    self.item.user.save()

    tz1_quantity = Inventory.objects.get_expired(self.item)

    self.item.user.timezone = timezone2
    self.item.user.save()

    tz2_quantity = Inventory.objects.get_expired(self.item)

    self.assertNotEqual(
        tz1_quantity,
        tz2_quantity,
    )

  def test_utc_w_usage(self):
    quantity = 30.1
    usage_quantity = -1

    scenarios = self._create_scenarios(quantity)
    usage_scenarios = self._create_scenarios(usage_quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])
    self._create_test_transaction(**usage_scenarios['today'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, quantity * 2 + usage_quantity)

  def test_utc_no_expired_items(self):
    quantity = 20.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_expired(self.item)
    self.assertEqual(received_quantity, 0)


class TestGetInventoryExpirationDatetime(ExpirationManagerTestHarness):
  """Test the `ExpirationManager.get_inventory_expiration_datetime` method."""

  def test_utc(self):
    self.item.user.timezone = "UTC"
    self.item.user.save()

    expected_date = (
        pendulum.now(tz=self.item.user.timezone) -
        timedelta(days=self.item.shelf_life)
    ).start_of('day')

    received_data = Inventory.objects.get_inventory_expiration_datetime(
        self.item
    )

    self.assertEqual(received_data, expected_date)

  def test_honolulu(self):
    self.item.user.timezone = "Pacific/Honolulu"
    self.item.user.save()

    expected_date = (
        pendulum.now(tz=self.item.user.timezone) -
        timedelta(days=self.item.shelf_life)
    ).start_of('day')

    received_data = Inventory.objects.get_inventory_expiration_datetime(
        self.item
    )

    self.assertEqual(received_data, expected_date)

  def test_tz_diff(self):
    timezone1 = "Pacific/Honolulu"
    timezone2 = "UTC"

    self.item.user.timezone = timezone2
    self.item.user.save()

    tz2_datetime = Inventory.objects.get_inventory_expiration_datetime(
        self.item
    )

    self.item.user.timezone = timezone1
    self.item.user.save()

    tz1_datetime = Inventory.objects.get_inventory_expiration_datetime(
        self.item
    )

    self.assertEqual((tz2_datetime - tz1_datetime).days, 0)
    self.assertEqual((tz2_datetime.date() - tz1_datetime.date()).days, 1)


class TestGetNextExpiryDatetime(ExpirationManagerTestHarness):
  """Test the `ExpirationManager.get_next_expiry_datetime` method."""

  def test_utc(self):
    test_timezone = "UTC"

    user = self.item.user
    user.timezone = test_timezone
    user.save()

    scenarios = self._create_scenarios(30.1)
    self._create_test_transaction(**scenarios['today'])
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['last_year'])

    expiry_datetime = self._user_expiry_datetime(self.item, self.one_month_ago)
    received_datetime = Inventory.objects.get_next_expiry_datetime(self.item)

    self.assertEqual(
        expiry_datetime,
        received_datetime,
    )

    self.assertEqual(received_datetime.tzname(), pytz.utc.zone)
    self.assertEqual(received_datetime.hour, 0)
    self.assertEqual(received_datetime.hour, 0)
    self.assertEqual(received_datetime.minute, 0)
    self.assertEqual(received_datetime.second, 0)

  def test_honolulu(self):
    test_timezone = "Pacific/Honolulu"

    user = self.item.user
    user.timezone = test_timezone
    user.save()

    scenarios = self._create_scenarios(30.1)
    self._create_test_transaction(**scenarios['today'])
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['last_year'])

    received_datetime = Inventory.objects.get_next_expiry_datetime(self.item)
    received_in_user_time = received_datetime.astimezone(user.timezone)

    self.assertNotEqual(received_datetime.hour, 0)
    self.assertEqual(received_datetime.tzname(), pytz.utc.zone)

    self.assertEqual(received_in_user_time.tzinfo, self._user_tzinfo(user))
    self.assertEqual(received_in_user_time.hour, 0)
    self.assertEqual(received_in_user_time.minute, 0)
    self.assertEqual(received_in_user_time.second, 0)

  def test_tz_diff(self):
    scenarios = self._create_scenarios(10.1)
    self._create_test_transaction(**scenarios['today'])

    timezone1 = "Pacific/Honolulu"
    timezone2 = "Asia/Hong_Kong"

    self.item.user.timezone = timezone2
    self.item.user.save()
    tz2_datetime = Inventory.objects.get_next_expiry_datetime(self.item)

    self.item.user.timezone = timezone1
    self.item.user.save()
    tz1_datetime = Inventory.objects.get_next_expiry_datetime(self.item)

    self.assertNotEqual(tz1_datetime, tz2_datetime)
    self.assertNotEqual(tz1_datetime.hour, tz2_datetime.hour)

    self.assertEqual(tz1_datetime.tzname(), pytz.utc.zone)
    self.assertEqual(tz2_datetime.tzname(), pytz.utc.zone)

  def test_no_unexpired_items(self):
    scenarios = self._create_scenarios(20.1)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    expiry_datetime = None
    received_datetime = Inventory.objects.get_next_expiry_datetime(self.item)

    self.assertEqual(
        expiry_datetime,
        received_datetime,
    )


class TestGetNextExpiryQuantity(ExpirationManagerTestHarness):
  """Test the `ExpirationManager.get_next_expiry_quantity` method."""

  def test_utc(self):
    quantity = 30.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['timezone_edgecase'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity * 2)

  def test_honolulu(self):
    quantity = 30.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['last_month'])
    self._create_test_transaction(**scenarios['timezone_edgecase'])

    self.item.user.timezone = "Pacific/Honolulu"
    self.item.user.save()

    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity)

  def test_tz_diff(self):
    scenarios = self._create_scenarios(10.1)
    self._create_test_transaction(**scenarios['timezone_edgecase'])

    timezone1 = "UTC"
    timezone2 = "Pacific/Honolulu"

    self.item.user.timezone = timezone1
    self.item.user.save()

    tz1_quantity = Inventory.objects.get_next_expiry_quantity(self.item)

    self.item.user.timezone = timezone2
    self.item.user.save()

    tz2_quantity = Inventory.objects.get_next_expiry_quantity(self.item)

    self.assertNotEqual(
        tz1_quantity,
        tz2_quantity,
    )

  def test_utc_w_consumption(self):
    quantity = 30.1
    usage_quantity = -1

    scenarios = self._create_scenarios(quantity)
    usage_scenarios = self._create_scenarios(usage_quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**usage_scenarios['today'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity + usage_quantity)

  def test_utc_w_aggregation(self):
    quantity = 20.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_week'])
    self._create_test_transaction(**scenarios['last_month'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, quantity)

  def test_utc_no_unexpired_items(self):
    quantity = 10.1

    scenarios = self._create_scenarios(quantity)
    self._create_test_transaction(**scenarios['last_year'])
    self._create_test_transaction(**scenarios['last_year_and_a_day'])

    self.item.user.timezone = "UTC"
    self.item.user.save()

    received_quantity = Inventory.objects.get_next_expiry_quantity(self.item)
    self.assertEqual(received_quantity, 0)
