"""Base classes for kitchen model test fixtures."""

from abc import ABC, abstractmethod

from django.forms import model_to_dict
from django.test import TestCase

from ...signals.transaction import transaction_post_save_handler
from .fixture_mixins import MutableSignalsMixin


class KitchenModelTestFixture(ABC):
  """Define the ABC for the kitchen model fixtures."""

  create_data: dict
  calculated_properties: set
  m2m_fields: set

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

  def setUp(self):
    self.objects = list()

  def tearDown(self):
    for obj in self.objects:
      if obj.id:
        obj.delete()

  def _instance_to_dict(self, instance, exclude=()):
    representation = model_to_dict(instance, exclude=exclude)
    for property_name in self.calculated_properties:
      representation[property_name] = getattr(instance, property_name)
    for m2m in self.m2m_fields:
      representation[m2m] = [obj.id for obj in getattr(instance, m2m).all()]
    return representation

  def _instance_to_dict_subset(self, instance, filter_dict):
    fields = set(filter_dict.keys())
    model_fields = set(f.name for f in instance._meta.fields)
    exclude_fields = model_fields ^ fields

    return self._instance_to_dict(instance, exclude=exclude_fields)


class MutableSignalsBaseTestCase(MutableSignalsMixin, TestCase):
  """Extends the `django.tests.TestCase` with the MutableSignalsMixin."""

  registered_signals = [{
      'signal_name': 'post_save',
      'handler': transaction_post_save_handler,
      'sender': 'kitchen.Transaction',
  }]
