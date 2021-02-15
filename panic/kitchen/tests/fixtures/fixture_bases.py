"""Base classes for kitchen model test fixtures."""

from abc import ABC, abstractmethod


class KitchenModelTestFixture(ABC):
  """Define the Abstract Base Class for the kitchen model fixtures."""

  @staticmethod
  @abstractmethod
  def create_instance(**kwargs):
    pass

  @staticmethod
  @abstractmethod
  def create_dependencies(seed, **kwargs):
    pass

  @classmethod
  @abstractmethod
  def create_data_hook(cls):
    pass

  @abstractmethod
  def create_test_instance(self, **kwargs):
    pass

  @classmethod
  @abstractmethod
  def setUpTestData(cls):
    pass

  @abstractmethod
  def setUp(self):
    pass

  @abstractmethod
  def tearDown(self):
    pass
