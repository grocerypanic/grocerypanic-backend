"""Base classes for kitchen model test fixtures."""

from abc import ABC, abstractmethod

from django.test import TestCase

from ...signals.transaction import transaction_post_save_handler
from .fixture_mixins import MutableSignalsMixin


class KitchenModelTestFixture(ABC):
  """Define the Abstract Base Class for the kitchen model fixtures."""

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


class MutableSignalsBaseTestCase(MutableSignalsMixin, TestCase):
  """Extends the `django.tests.TestCase` with the MutableSignalsMixin."""

  registered_signals = [{
      'signal_name': 'post_save',
      'handler': transaction_post_save_handler,
      'sender': 'kitchen.Transaction',
  }]
