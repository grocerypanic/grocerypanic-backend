"""Test the Custom Caching Decorators."""

from datetime import datetime

import pendulum
from django.test import SimpleTestCase
from django.utils.timezone import now
from freezegun import freeze_time

from ..caching import (
    SETTER_ERROR,
    PersistentCachedProperty,
    PersistentModelFieldCache,
)


class TestCachingDecoratorNonTTLRelated(SimpleTestCase):
  """Test the PersistentCachedProperty class for non TTL bounded conditions."""

  def setUp(self):
    self.initial_value = 0
    self.instance1 = Model(1, self.initial_value, None)

  def test_cached_calculation_base(self):
    self.assertIsInstance(
        self.instance1.__class__.__dict__['cached_calculated'],
        PersistentModelFieldCache,
    )

  def test_calculation(self):
    self.assertEqual(self.instance1.calculation(), self.initial_value + 1)

    self.instance1.increment_cached_value()

    self.assertNotEqual(
        self.instance1.calculation,
        self.initial_value + 1,
    )

  def test_setter_error(self):
    with self.assertRaises(AttributeError) as raised:
      self.instance1.cached_calculated = 1

    self.assertEqual(
        raised.exception.args,
        (SETTER_ERROR,),
    )

  def test_ttl_field_is_None(self):
    result1 = self.instance1.alias_calculation

    self.assertEqual(
        result1,
        self.initial_value + 1,
    )

    self.instance1.increment_cached_value()
    is_cached = (self.instance1.cached_calculated == self.initial_value + 1)

    self.assertFalse(is_cached,)


# pylint: disable=comparison-with-callable,protected-access
@freeze_time("2020-01-14")
class TestCachingDecoratorTTLTestHarness(SimpleTestCase):
  """Test the PersistentCachedProperty class."""

  __test__ = False
  ttl_until: datetime

  def setUp(self):
    self.ttl_valid = self.ttl_until > now()
    self.initial_value = 0
    self.instance1 = Model(1, self.initial_value, self.ttl_until)
    self.instance2 = Model(2, self.initial_value + 1, self.ttl_until)

  def test_caching_is_dependent_on_ttl(self):
    result1 = self.instance1.cached_calculated

    self.assertEqual(
        result1,
        self.initial_value + 1,
    )

    self.instance1.increment_cached_value()
    is_cached = (self.instance1.cached_calculated == self.initial_value + 1)

    self.assertEqual(
        is_cached,
        self.ttl_valid,
    )

  def test_model_save_count_is_dependent_on_ttl(self):
    self.assertEqual(
        self.instance1._save_calls,
        0,
    )

    response1 = self.instance1.cached_calculated
    self.instance1.increment_cached_value()
    is_cached = response1 == self.instance1.cached_calculated
    expected_count = 1 if is_cached else 2

    self.assertEqual(
        self.instance1._save_calls,
        expected_count,
    )

  def test_model_save_only_if_value_is_different(self):
    self.assertEqual(
        self.instance1._save_calls,
        0,
    )

    response1 = self.instance1.cached_calculated
    response2 = self.instance1.cached_calculated

    values_match = response1 == response2
    expected_count = 1

    self.assertTrue(values_match)

    self.assertEqual(
        self.instance1._save_calls,
        expected_count,
    )

  def test_alias_calculation_caching_is_dependent_on_ttl(self):
    result1 = self.instance1.alias_calculation

    self.assertEqual(
        result1,
        self.initial_value + 1,
    )

    self.instance1.increment_cached_value()
    is_cached = (self.instance1.alias_calculation == result1)

    self.assertEqual(
        is_cached,
        self.ttl_valid,
    )

  def test_cached_calculation_invalidation(self):
    result1 = self.instance1.cached_calculated

    self.assertEqual(
        result1,
        self.initial_value + 1,
    )

    self.instance1.increment_cached_value()
    del self.instance1.cached_calculated
    is_cached = (self.instance1.cached_calculated == self.initial_value + 1)

    self.assertFalse(is_cached)

  def test_cached_calculation_multiple_instances(self):
    result1 = self.instance1.cached_calculated
    result2 = self.instance2.cached_calculated

    self.assertEqual(
        result1,
        self.initial_value + 1,
    )

    self.instance1.increment_cached_value()

    is_cached = (self.instance1.cached_calculated == self.initial_value + 1)
    is_independent = (self.instance2.cached_calculated == result2)

    self.assertEqual(
        is_cached,
        self.ttl_valid,
    )

    self.assertEqual(
        is_independent and is_cached,
        self.ttl_valid,
    )


class TestCachingDecoratorTTLValid(TestCachingDecoratorTTLTestHarness):
  """Test the PersistentCachedProperty class while TTL is valid."""

  __test__ = True
  ttl_until = pendulum.datetime(year=2020, month=1, day=15, tz="UTC")


class TestCachingDecoratorTTLInvalid(TestCachingDecoratorTTLTestHarness):
  """Test the PersistentCachedProperty class while TTL is invalid."""

  __test__ = True
  ttl_until = pendulum.datetime(year=2020, month=1, day=14, tz="UTC")


class Model:
  """A mock model for testing."""

  def __init__(self, instance_id, initial, expiry):
    self.id = instance_id
    self.initial = initial
    self.expiry_date = expiry
    self._cached_calculated = None
    self._save_calls = 0

  def save(self):
    self._save_calls += 1

  def increment_cached_value(self):
    self.initial += 1

  @property
  def get_expiry_date(self):
    return self.expiry_date

  def calculation(self):
    return self.initial + 1

  @PersistentCachedProperty(
      ttl_field="get_expiry_date",
      cached_field="_cached_calculated",
  )
  def alias_calculation(self):
    return self.calculation()

  @PersistentCachedProperty(ttl_field="get_expiry_date")
  def cached_calculated(self):
    return self.calculation()
