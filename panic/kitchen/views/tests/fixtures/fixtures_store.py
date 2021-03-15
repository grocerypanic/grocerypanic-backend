"""Test harness for the Store API ViewSet."""

from ....tests.fixtures.fixtures_store import StoreTestHarness


class AnotherUserTestHarness(StoreTestHarness):
  """Extend the test harness by adding an additional user."""

  @classmethod
  def create_data_hook(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']
