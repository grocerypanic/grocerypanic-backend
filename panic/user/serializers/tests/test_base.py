"""Test the UserBase serializer implements all methods."""

from unittest.mock import patch

from django.test import SimpleTestCase

from .. import bases
from ..bases import UserBase

BASES_MODULE = bases.__name__


class TestBase(SimpleTestCase):
  """Test the UserBase serializer implements all methods."""

  def setUp(self):
    self.test_value = "ExpectedValue"

  @patch(BASES_MODULE + ".serializers.Serializer.create")
  def test_create_is_noop(self, base_create):
    base_create.return_value = self.test_value
    serializer = UserBase(data={})
    return_value = serializer.create(validated_data={})
    base_create.assert_called_once()
    self.assertEqual(return_value, self.test_value)

  @patch(BASES_MODULE + ".serializers.Serializer.update")
  def test_update_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = UserBase(data={})
    return_value = serializer.update(instance={}, validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)
