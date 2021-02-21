"""Mixin classes for kitchen model test fixtures."""

from django.core.exceptions import ValidationError
from django.db.models import signals as django_signals
from rest_framework import serializers


class ModelTestMixin:
  """Mixin class for model testing.

  Mix with a class that inherits from::
    - a concrete implementation of :class:`kitchen.tests.fixtures.fixture_bases.
      KitchenModelTestFixture`
    - :class:`django.test.TestCase`
  """

  create_data: dict
  fields: dict

  @staticmethod
  def generate_overload(fields):
    return_value = []
    for key, value in fields.items():
      return_value.append({key: "abc" * value})
    return return_value

  def test_field_lengths(self):
    for overloaded_field in self.generate_overload(self.fields):
      local_data = dict(self.create_data)
      local_data.update(overloaded_field)
      with super().assertRaises(ValidationError):
        _ = super().create_test_instance(**local_data)


class MutableSignalsMixin:
  """Mixin class for adding mutable signal control to test classes.

  Mix with a class that inherits from::
    - :class:`django.test.TestCase`
  """

  mute_signals: bool = True
  registered_signals: list = []

  @classmethod
  def _toggle_signal(cls, action, **kwargs):
    signal = getattr(django_signals, kwargs['signal_name'])
    toggle = getattr(signal, action)
    toggle(kwargs['handler'], sender=kwargs['sender'])

  @classmethod
  def setUpClass(cls):
    if cls.mute_signals:
      for signal_definition in cls.registered_signals:
        cls._toggle_signal('disconnect', **signal_definition)
    super().setUpClass()

  @classmethod
  def tearDownClass(cls):
    if cls.mute_signals:
      for signal_definition in cls.registered_signals:
        cls._toggle_signal('connect', **signal_definition)
    super().tearDownClass()


class SerializerTestMixin:
  """Mixin class for serializer testing.

  Mix with a class that inherits from::
    - :class:`django.test.TestCase`
  """

  create_data: dict
  fields: dict
  request: object
  serializer: serializers.Serializer

  @staticmethod
  def generate_overload(fields):
    return_value = []
    for key, value in fields.items():
      return_value.append({key: "abc" * value})
    return return_value

  def test_field_lengths(self):
    overloads = self.generate_overload(self.fields)
    for overload in overloads:
      local_data = dict(self.create_data)
      local_data.update(overload)
      with super().assertRaises(serializers.ValidationError):
        serialized = self.serializer(
            context={'request': self.request},
            data=local_data,
        )
        serialized.is_valid(raise_exception=True)
