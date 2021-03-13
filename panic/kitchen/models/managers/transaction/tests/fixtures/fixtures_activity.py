"""Test harness for the Transaction Activity model manager."""

import random
from collections import OrderedDict
from datetime import timedelta

from django.utils import timezone

from ......tests.fixtures.fixtures_transaction import TransactionTestHarness


class ActivityManagerTestHarness(TransactionTestHarness):
  """Test harness for the Transaction Activity model manager."""

  randomize_datetimes = False
  user2_initial_transaction = True
  mute_signals = False

  user2: object
  item2: object

  dates: OrderedDict
  initial_transaction1: dict
  transaction_quantity: float

  @classmethod
  def setUpTestData(cls):
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']
    super().setUpTestData()

  @classmethod
  def create_transaction_history(cls, pattern):
    cls._create_initial_item_quantities()
    for value in cls.dates.values():
      for quantity in pattern:
        cls._create_randomized_instance(
            item=cls.item1,
            date_object=value,
            user=cls.user1,
            quantity=quantity,
        )

  @classmethod
  def _create_randomized_instance(cls, **kwargs):
    modified = dict(kwargs)
    if cls.randomize_datetimes:
      offset = random.randint(0, 9600)
      modified.update({
          'date_object': kwargs['date_object'] + timedelta(seconds=offset)
      })
    return cls.create_instance(**modified)

  @classmethod
  def _create_initial_item_quantities(cls):
    cls._create_randomized_instance(**cls.initial_transaction1)
    if cls.user2_initial_transaction:
      cls.initial_transaction2 = dict(cls.initial_transaction1)
      cls.initial_transaction2.update({
          'item': cls.item2,
      })
      cls._create_randomized_instance(**cls.initial_transaction2)

  @classmethod
  def _create_another_user_transaction(cls):
    cls._create_randomized_instance(
        item=cls.item2,
        date_object=cls.dates['today'],
        user=cls.user2,
        quantity=cls.transaction_quantity,
    )

  @classmethod
  def _create_lower_bounds_edge_case_transaction(cls, age_in_days):
    cls.dates['edge_case'] = cls._create_edge_case_date(age_in_days)
    purchase = cls.transaction_quantity
    consumption = -1 * cls.transaction_quantity
    for quantity in [purchase, consumption, consumption, consumption]:
      cls.create_instance(
          item=cls.item1,
          date_object=cls.dates['edge_case'],
          user=cls.user1,
          quantity=quantity,
      )

  @staticmethod
  def _create_edge_case_date(age_in_days):
    return (
        timezone.now() - (timedelta(days=age_in_days,) + timedelta(hours=1,))
    )

  def create_test_edge_case(self, age_in_days):
    self.create_test_instance(
        item=self.item1,
        date_object=self._create_edge_case_date(age_in_days),
        user=self.user1,
        quantity=-1 * self.transaction_quantity,
    )
