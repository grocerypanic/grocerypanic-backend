"""Test the TimeZone serializer implements all methods."""

from unittest.mock import patch

from django.test import SimpleTestCase

from .. import timezones
from ..timezones import TimezoneSerializer

MODULE = timezones.__name__


class TestMethods(SimpleTestCase):
  """Test the TimeZone serializer implements all methods."""

  def setUp(self):
    self.test_value = "ExpectedValue"

  @patch(MODULE + ".serializers.Serializer.create")
  def test_create_is_noop(self, base_create):
    base_create.return_value = self.test_value
    serializer = TimezoneSerializer(data={})
    return_value = serializer.create(validated_data={})
    base_create.assert_called_once()
    self.assertEqual(return_value, self.test_value)

  @patch(MODULE + ".serializers.Serializer.update")
  def test_update_is_noop(self, base_update):
    base_update.return_value = self.test_value
    serializer = TimezoneSerializer(data={})
    return_value = serializer.update(instance={}, validated_data={})
    base_update.assert_called_once()
    self.assertEqual(return_value, self.test_value)


class TestData(SimpleTestCase):
  """Test the TimeZone serializer serializes data correctly."""

  def setUp(self):
    self.test_value = {"id": 3, "name": "mock_zone"}

  def test_serialize(self):
    data = TimezoneSerializer([self.test_value], many=True)

    self.assertDictEqual(
        data.data[0], {
            "id": self.test_value["id"],
            "name": self.test_value["name"],
        }
    )
