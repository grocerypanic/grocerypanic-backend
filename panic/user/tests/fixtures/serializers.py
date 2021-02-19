"""Base Classes for Serializer Test Fixtures"""

from django.db import models
from django.test import TestCase
from rest_framework import serializers


# pylint disable=too-many-instance-attributes
class SerializerTestHarness(TestCase):
  __test__ = False
  serializer: serializers.Serializer
  model: models.Model

  deserializer_data: dict
  serializer_data_invalid: list
  serializer_data: dict

  request: object
  serializer_data_field: str
  serializer_operations: object
  deserializer_operations: object
  context: dict

  @staticmethod
  def __noop(value):
    return value

  def create_data_hook(self):
    pass

  def setUp(self):
    self.create_data_hook()
    self.objects = []

  def tearDown(self):
    for obj in self.objects:
      obj.delete()

  def assertDataEqualsInstance(
      self,
      data_dict,
      instance,
  ):
    for prop, value in data_dict.items():
      operation = self.__noop
      if hasattr(self.deserializer_operations, prop):
        operation = getattr(self.deserializer_operations, prop)
      self.assertEqual(
          operation(getattr(instance, prop)),
          value,
      )

  def assertDataEqualsSerialized(
      self,
      data_dict,
      serialized_dict,
  ):

    for prop, value in serialized_dict.items():
      operation = self.__noop
      if hasattr(self.serializer_operations, prop):
        operation = getattr(self.serializer_operations, prop)
      self.assertEqual(
          data_dict.get(prop),
          operation(value),
      )

  def create_test_instance(self, **kwargs):
    """Create a test item."""
    instance = self.model.objects.create(**kwargs)
    self.objects.append(instance)
    return instance

  @staticmethod
  def generate_overload(fields):
    return_list = []
    for key, value in fields.items():
      overloaded = dict()
      overloaded[key] = "abc" * value
      return_list.append(overloaded)
    return return_list

  def testDeserialize(self, mock_validate=None):
    instance = self.create_test_instance(**self.deserializer_data)
    serialized = self.serializer(instance)
    deserialized = serialized.data

    self.assertDataEqualsInstance(deserialized, instance)

    if mock_validate:
      mock_validate.assert_not_called()

  def testSerialize(self, mock_validate=None):
    if mock_validate:
      mock_validate.return_value = self.serializer_data

    serialized = self.serializer(
        context=self.context,
        data=self.serializer_data,
    )
    serialized.is_valid(raise_exception=True)

    self.assertDataEqualsSerialized(serialized.data, self.serializer_data)

    if mock_validate:
      mock_validate.assert_called_once()

  def testSerializeInvalidData(self, mock_validate=None):
    for invalid_data in self.serializer_data_invalid:
      serialized = self.serializer(
          context=self.context,
          data=invalid_data,
      )
      with self.assertRaises(serializers.ValidationError):
        serialized.is_valid(raise_exception=True)

    if mock_validate:
      mock_validate.assert_not_called()

  def testFieldLengths(self, mock_validate=None):
    overloads = self.generate_overload(self.fields)
    for overload in overloads:
      with self.assertRaises(serializers.ValidationError):
        serialized = self.serializer(
            context=self.context,
            data=overload,
        )
        serialized.is_valid(raise_exception=True)

    if mock_validate:
      mock_validate.assert_not_called()
