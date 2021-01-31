"""Abstract Base Class for Kitchen Model Test Fixtures"""

from abc import ABC, abstractmethod


class KitchenModelTestFixture(ABC):

  @staticmethod
  @abstractmethod
  def create_instance(**kwargs):
    pass

  @staticmethod
  @abstractmethod
  def create_dependencies(seed):
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
