"""Test the base serializer implements all methods."""

from unittest.mock import patch

from django.test import TestCase

from .. import bases
from ..bases import CustomUserBase


class TestBase(TestCase):

  @classmethod
  def setUpTestData(cls):
    cls.test_value = "ExpectedValue"

  @patch(bases.__name__ + ".serializers.Serializer.create")
  def test_create_is_noop(self, base_create):
    base_create.return_value = self.test_value
    serializer = CustomUserBase(data={})
    return_value = serializer.create(validated_data={})
    base_create.assert_called_once()
    self.assertEqual(return_value, self.test_value)

  @patch(bases.__name__ + ".serializers.Serializer.update")
  def test_update_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = CustomUserBase(data={})
    return_value = serializer.update(instance={}, validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)
