"""Test harness for the Transaction API ViewSet."""

from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from freezegun import freeze_time

from ....models.item import Item
from ....tests.fixtures.fixtures_transaction import TransactionTestHarness


class TransactionViewSetHarness(TransactionTestHarness):
  """Extend the TransactionTestHarness class by adding test data."""

  item2: Item
  user2: AbstractUser

  mute_signals = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()

  @classmethod
  @freeze_time("2020-01-14")
  def create_data_hook(cls):
    test_data = cls.create_dependencies(2)
    cls.user2 = test_data['user']
    cls.store2 = test_data['store']
    cls.shelf2 = test_data['shelf']
    cls.item2 = test_data['item']

    cls.one_second_from_now = timezone.now() + timezone.timedelta(seconds=1)
    cls.two_seconds_from_now = timezone.now() + timezone.timedelta(seconds=2)
    cls.eleven_days_ago = timezone.now() - timezone.timedelta(days=11)
    cls.serializer_data = {'item': cls.item1.id, 'quantity': 3}

    cls.transaction_now = {
        'user': cls.user1,
        'date_object': timezone.now(),
        'item': cls.item1,
        'quantity': 5
    }
    cls.transaction_one_second = {
        'user': cls.user1,
        'date_object': cls.one_second_from_now,
        'item': cls.item1,
        'quantity': 5
    }
    cls.transaction_two_seconds_another_item = {
        'user': cls.user2,
        'date_object': cls.two_seconds_from_now,
        'item': cls.item2,
        'quantity': 5
    }
    cls.transaction_eleven_days_ago = {
        'user': cls.user1,
        'date_object': cls.eleven_days_ago,
        'item': cls.item1,
        'quantity': 5
    }

    cls.serializer_data_wrong_item = {'item': cls.item2.id, 'quantity': 3}
