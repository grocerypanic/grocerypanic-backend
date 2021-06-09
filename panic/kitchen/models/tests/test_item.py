"""Test the Item model."""
# pylint: disable=protected-access

import datetime
from unittest.mock import MagicMock, patch

import pendulum
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.functional import cached_property
from freezegun import freeze_time

from utilities.models.decorators.caching import PersistentCachedProperty
from ...tests.fixtures.fixture_mixins import ModelTestMixin
from ...tests.fixtures.fixtures_item import ItemTestHarness
from .. import constants
from .. import item as item_module
from ..item import Item

ITEM_MODULE = item_module.__name__


class TestItem(ModelTestMixin, ItemTestHarness):
  """Test the Item model."""

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.fields = {"name": 255}
    cls.create_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
    }

  def test_create(self):
    created = self.create_test_instance(**self.create_data)
    query = Item.objects.filter(name=self.create_data['name'])

    self.assertQuerysetEqual(query, [created])
    self.assertEqual(query[0]._index, self.create_data['name'].lower())

  def test_unique(self):
    _ = self.create_test_instance(**self.create_data)

    case_data = dict(self.create_data)
    case_data.update({
        'name': self.create_data['name'].lower(),
    })

    with self.assertRaises(ValidationError):
      _ = self.create_test_instance(**case_data)

    count = Item.objects.filter(name__iexact=self.create_data['name']).count()
    assert count == 1

  def test_bleach(self):
    injection_attack = dict(self.create_data)
    injection_attack['name'] = "Canned Beans<script>alert('hi');</script>"
    sanitized_name = "Canned Beans&lt;script&gt;alert('hi');&lt;/script&gt;"

    _ = self.create_test_instance(**injection_attack)

    query = Item.objects.filter(name=injection_attack['name']).count()
    assert query == 0

    query = Item.objects.filter(name=sanitized_name)
    assert len(query) == 1

    item = query[0]
    self.assertEqual(item._index, sanitized_name.lower())
    self.assertEqual(item.name, sanitized_name)
    self.assertEqual(item.shelf_life, self.create_data['shelf_life'])
    self.assertEqual(item.user.id, self.user1.id)
    self.assertEqual(item.shelf.id, self.shelf1.id)
    self.assertEqual(item.price, self.create_data['price'])

  def test_str(self):
    item = self.create_test_instance(**self.create_data)
    self.assertEqual(self.create_data['name'], str(item))

  def test_lower_bound_shelf_life(self):
    item = self.create_test_instance(**self.create_data)
    item.shelf_life = Item.MINIMUM_SHELF_LIFE - 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_upper_bound_shelf_life(self):
    item = self.create_test_instance(**self.create_data)
    item.shelf_life = Item.MAXIMUM_SHELF_LIFE + 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_two_users_with_the_same_item_name(self):
    item1 = self.create_test_instance(**self.create_data)

    self.create_second_test_set()
    second_item_data = dict(self.create_data)
    second_item_data['user'] = self.user2
    second_item_data['shelf'] = self.shelf2
    second_item_data['preferred_stores'] = [self.store2]
    item2 = self.create_test_instance(**second_item_data)

    self.assertEqual(item1.name, item2.name)
    self.assertNotEqual(item1, item2)

  def test_default_fraction_bool(self):
    item1 = self.create_test_instance(**self.create_data)
    self.assertFalse(item1.has_partial_quantities)

  def test_toggle_fraction_bool(self):
    item1 = self.create_test_instance(**self.create_data)
    item1.has_partial_quantities = True
    item1.save()
    self.assertTrue(item1.has_partial_quantities)

  def test_lower_bound_quantity(self):
    item = self.create_test_instance(**self.create_data)
    item.quantity = constants.MINIMUM_QUANTITY - 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_upper_bound_quantity(self):
    item = self.create_test_instance(**self.create_data)
    item.quantity = constants.MAXIMUM_QUANTITY + 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_lower_bound__expired(self):
    item = self.create_test_instance(**self.create_data)
    item._expired = constants.MINIMUM_QUANTITY - 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_upper_bound__expired(self):
    item = self.create_test_instance(**self.create_data)
    item._expired = constants.MAXIMUM_QUANTITY + 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_lower_bound__next_expiry_quantity(self):
    item = self.create_test_instance(**self.create_data)
    item._next_expiry_quantity = constants.MINIMUM_QUANTITY - 1
    with self.assertRaises(ValidationError):
      item.save()

  def test_upper_bound__next_expiry_quantity(self):
    item = self.create_test_instance(**self.create_data)
    item._next_expiry_quantity = constants.MAXIMUM_QUANTITY + 1
    with self.assertRaises(ValidationError):
      item.save()


@freeze_time("2020-01-14")
class TestItemCalculatedPropertiesInventory(ItemTestHarness):
  """Test the Item model's calculated properties that use Inventory."""

  @classmethod
  def create_data_hook(cls):
    cls.today = timezone.now()
    cls.data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
    }

    cls.item1 = cls.create_instance(**cls.data)

  def setUp(self):
    super().setUp()
    self.user1.timezone = "UTC"
    self.user1.save()
    self.item1.invalidate_caches()

  def test_refresh_from_db_clears_cache(self):
    persistent_cached_props = []
    django_cached_props = []

    for key, value in self.item1.__class__.__dict__.items():
      if isinstance(value, cached_property):
        django_cached_props.append(key)

    for key, value in self.item1.__class__.__dict__.items():
      if isinstance(value, PersistentCachedProperty):
        persistent_cached_props.append(key)

    self.assertNotEqual(0, len(django_cached_props))
    self.assertNotEqual(0, len(persistent_cached_props))

    cached_props = django_cached_props + persistent_cached_props

    with patch(ITEM_MODULE + ".delattr", MagicMock()) as m_del:
      self.item1.invalidate_caches()
      self.assertEqual(m_del.call_count, len(cached_props))
      for cached_prop in cached_props:
        m_del.assert_any_call(self.item1, cached_prop)

  @patch(ITEM_MODULE + ".Inventory.objects.get_expired")
  def test_expired(self, m_func):
    m_func.return_value = 1.1
    self.assertEqual(self.item1.expired, m_func.return_value)
    m_func.assert_called_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_expired")
  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_expired_is_cached(self, m_datetime, m_func):
    original_value = 1.1

    m_datetime.return_value = self.today - datetime.timedelta(days=3)
    m_func.return_value = original_value
    self.assertEqual(self.item1.expired, original_value)

    m_func.return_value = original_value + 1
    m_datetime.return_value = self.today + datetime.timedelta(days=3)
    del self.item1.next_expiry_datetime

    self.assertEqual(self.item1.expired, original_value)
    m_func.assert_called_once_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_date_utc(self, m_func):
    self.user1.timezone = "UTC"
    self.user1.save()

    m_func.return_value = timezone.now()
    user_adjusted_date = timezone.now().astimezone(self.user1.timezone).date()

    received_date = self.item1.next_expiry_date

    self.assertEqual(received_date, user_adjusted_date)
    self.assertIsInstance(received_date, datetime.date)
    m_func.assert_called_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_date_honolulu(self, m_func):
    self.user1.timezone = "Pacific/Honolulu"
    self.user1.save()

    m_func.return_value = timezone.now()
    user_adjusted_date = timezone.now().astimezone(self.user1.timezone).date()

    received_date = self.item1.next_expiry_date

    self.assertEqual(received_date, user_adjusted_date)
    self.assertIsInstance(received_date, datetime.date)
    m_func.assert_called_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_date_utc_w_no_expiry_objects(self, m_func):
    self.user1.timezone = "UTC"
    self.user1.save()

    m_func.return_value = None

    received_date = self.item1.next_expiry_date

    self.assertEqual(received_date, None)
    m_func.assert_called_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_date_tz_diff(self, m_func):
    m_func.return_value = timezone.now()

    self.user1.timezone = "Pacific/Honolulu"
    self.user1.save()
    tz1_date = self.item1.next_expiry_date

    self.user1.timezone = "UTC"
    self.user1.save()
    tz2_date = self.item1.next_expiry_date

    self.assertNotEqual(tz1_date, tz2_date)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_datetime(self, m_func):
    m_func.return_value = timezone.now()
    self.assertEqual(self.item1.next_expiry_datetime, m_func.return_value)
    m_func.assert_called_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_datetime_is_cached(self, m_func):
    original_value = timezone.now()

    m_func.return_value = original_value
    self.assertEqual(self.item1.next_expiry_datetime, original_value)

    m_func.return_value = None
    self.assertEqual(self.item1.next_expiry_datetime, original_value)
    m_func.assert_called_once_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_quantity")
  def test_next_expiry_quantity(self, m_func):
    m_func.return_value = 85.1
    self.assertEqual(self.item1.next_expiry_quantity, m_func.return_value)
    m_func.assert_called_with(self.item1)

  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_quantity")
  @patch(ITEM_MODULE + ".Inventory.objects.get_next_expiry_datetime")
  def test_next_expiry_quantity_is_cached(self, m_datetime, m_func):
    original_value = 85.1

    m_datetime.return_value = self.today - datetime.timedelta(days=3)
    m_func.return_value = original_value
    self.assertEqual(self.item1.next_expiry_quantity, original_value)

    m_datetime.return_value = self.today + datetime.timedelta(days=3)
    m_func.return_value = original_value + 1
    del self.item1.next_expiry_datetime

    self.assertEqual(self.item1.next_expiry_quantity, original_value)
    m_func.assert_called_once_with(self.item1)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  def test_activity_first(self, m_activity):
    m_activity.return_value = self.today - datetime.timedelta(days=900)
    self.assertEqual(
        self.item1.activity_first,
        m_activity.return_value,
    )
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  def test_activity_first_is_cached(self, m_activity):
    original_value = self.today - datetime.timedelta(days=900)
    m_activity.return_value = original_value
    self.assertEqual(
        self.item1.activity_first,
        original_value,
    )

    m_activity.return_value = self.today
    self.assertEqual(
        self.item1.activity_first,
        original_value,
    )
    m_activity.assert_called_once_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_last_two_weeks')
  def test_activity_last_two_weeks(self, m_activity):
    m_activity.return_value = "MockQuerySet"
    self.assertEqual(
        self.item1.activity_last_two_weeks,
        m_activity.return_value,
    )
    m_activity.assert_called_with(self.item1.id, zone=self.user1.timezone.zone)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_avg_week(self, m_usage, m_activity):
    m_usage.return_value = 999

    m_activity.return_value = self.today - datetime.timedelta(days=900)
    weeks = (
        pendulum.instance(self.today) -
        pendulum.instance(m_activity.return_value)
    ).in_weeks() + 1

    expected = (float("{:.2f}".format(m_usage.return_value / weeks)))

    self.assertEqual(
        self.item1.usage_avg_week,
        expected,
    )
    m_usage.assert_called_with(self.item1.id)
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_avg_week_zero_edge(self, m_usage, m_activity):
    m_usage.return_value = 999
    m_activity.return_value = self.today

    expected = (float("{:.2f}".format(m_usage.return_value / 1)))

    self.assertEqual(
        self.item1.usage_avg_week,
        expected,
    )
    m_usage.assert_called_with(self.item1.id)
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_avg_week_none_edge(self, m_usage, m_activity):
    m_activity.return_value = None

    expected = 0

    self.assertEqual(
        self.item1.usage_avg_week,
        expected,
    )
    m_usage.assert_not_called()
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_avg_month(self, m_usage, m_activity):
    m_usage.return_value = 999
    m_activity.return_value = self.today - datetime.timedelta(days=900)

    weeks = (
        pendulum.instance(self.today) -
        pendulum.instance(m_activity.return_value)
    ).in_months() + 1

    expected = (float("{:.2f}".format(m_usage.return_value / weeks)))

    self.assertEqual(
        self.item1.usage_avg_month,
        expected,
    )
    m_usage.assert_called_with(self.item1.id)
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_avg_month_zero_edge(self, m_usage, m_activity):
    m_usage.return_value = 999
    m_activity.return_value = self.today

    expected = (float("{:.2f}".format(m_usage.return_value / 1)))

    self.assertEqual(
        self.item1.usage_avg_month,
        expected,
    )
    m_usage.assert_called_with(self.item1.id)
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_activity_first')
  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_avg_month_none_edge(self, m_usage, m_activity):
    m_activity.return_value = None

    expected = 0

    self.assertEqual(
        self.item1.usage_avg_month,
        expected,
    )
    m_usage.assert_not_called()
    m_activity.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_current_week')
  def test_usage_current_week(self, m_usage):
    m_usage.return_value = 999

    self.assertEqual(
        self.item1.usage_current_week,
        m_usage.return_value,
    )
    m_usage.assert_called_with(self.item1.id, zone=self.user1.timezone.zone)

  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_current_month')
  def test_usage_current_month(self, m_usage):
    m_usage.return_value = 999

    self.assertEqual(
        self.item1.usage_current_month,
        m_usage.return_value,
    )
    m_usage.assert_called_with(self.item1.id, zone=self.user1.timezone.zone)

  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_total(self, m_usage):
    m_usage.return_value = 999
    self.assertEqual(
        self.item1.usage_total,
        m_usage.return_value,
    )
    m_usage.assert_called_with(self.item1.id)

  @patch(ITEM_MODULE + '.Transaction.objects.get_usage_total')
  def test_usage_total_is_cached(self, m_usage):
    original_value = 999

    m_usage.return_value = original_value
    self.assertEqual(
        self.item1.usage_total,
        original_value,
    )

    m_usage.return_value = original_value + 1
    self.assertEqual(
        self.item1.usage_total,
        original_value,
    )
    m_usage.assert_called_once_with(self.item1.id)


class TestItemRelatedFields(ItemTestHarness):
  """Test the Item model's related fields."""

  @classmethod
  def create_data_hook(cls):
    cls.create_data = {
        'user': cls.user1,
        'name': "Canned Beans",
        'shelf_life': 99,
        'shelf': cls.shelf1,
        'preferred_stores': [cls.store1],
        'price': 2.00,
    }

  def setUp(self):
    super().setUp()
    self.create_second_test_set()

    self.create_data2 = {
        'user': self.user2,
        'name': "Organic Canned Beans",
        'shelf_life': 99,
        'shelf': self.shelf2,
        'preferred_stores': [self.store2],
        'price': 2.00,
    }

  def test_wrong_preferred_stores(self):
    wrong_related_item = dict(self.create_data)
    wrong_related_item.update({'preferred_stores': [self.store2]})

    with self.assertRaises(ValidationError) as raised:
      self.create_test_instance(**wrong_related_item)

    self.assertDictEqual(
        raised.exception.message_dict, {
            'user': ["This must match the 'preferred_stores' field."],
            'preferred_stores':
                ["These selections must match the 'user' field."],
        }
    )

  def test_wrong_shelf(self):
    wrong_related_item = dict(self.create_data)
    wrong_related_item.update({'shelf': self.shelf2})

    with self.assertRaises(ValidationError) as raised:
      self.create_test_instance(**wrong_related_item)

    self.assertDictEqual(
        raised.exception.message_dict, {
            'user': ["This must match the 'shelf' field."],
            'shelf': ["This field must match the 'user' field."],
        }
    )

  def test_deleting_shelf(self):
    item = self.create_test_instance(**self.create_data2)
    self.shelf2.delete()
    item.refresh_from_db()

    self.assertEqual(
        item.shelf,
        None,
    )

  def test_delete_store(self):
    created = self.create_test_instance(**self.create_data)
    self.store1.delete()

    self.assertEqual(
        created.preferred_stores.all().count(),
        0,
    )
