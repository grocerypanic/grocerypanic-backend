"""Tests for the M2MThroughSerializerField class."""

from unittest.mock import Mock

from django.test import SimpleTestCase

from ..m2m import M2MThroughSerializerField


class TestM2MThroughSerializerField(SimpleTestCase):
  """Test the M2MThroughSerializerField class."""

  def setUp(self):
    super().setUp()
    self.model = Mock()
    self.model.id = 2
    self.queryset = Mock()
    self.queryset.get.return_value = self.model

    self.field = M2MThroughSerializerField(queryset=self.queryset)

  def test_to_internal_int(self):
    result = self.field.to_internal_value(self.model.id)

    self.queryset.get.assert_called_with(pk=self.model.id)
    self.assertEqual(
        result,
        self.model,
    )

  def test_to_internal_str(self):
    result = self.field.to_internal_value(str(self.model.id))

    self.queryset.get.assert_called_with(pk=str(self.model.id))
    self.assertEqual(
        result,
        self.model,
    )

  def test_to_internal_instance(self):
    result = self.field.to_internal_value(self.model)

    self.queryset.get.assert_not_called()
    self.assertEqual(
        result,
        self.model,
    )

  def test_to_representation(self):
    result = self.field.to_representation(self.model)

    self.assertEqual(
        result,
        self.model.id,
    )
