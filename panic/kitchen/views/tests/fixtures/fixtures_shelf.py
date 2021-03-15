"""Test harness for the Shelf API ViewSet."""

from ....tests.fixtures.fixtures_shelf import ShelfTestHarness


class AnotherUserTestHarness(ShelfTestHarness):
  """Extend the test harness by adding an additional user."""

  @classmethod
  def create_data_hook(cls):
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']
