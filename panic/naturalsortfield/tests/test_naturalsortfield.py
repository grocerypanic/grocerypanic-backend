"""Test the NaturalSortField Django field."""

from unittest import TestCase, mock

from .. import fields
from ..fields import NaturalSortField

FIELDS_MODULE = fields.__name__


class TestNaturalSortFieldModelModeMethods(TestCase):
  """Test the NaturalSortField model methods."""

  def setUp(self):
    self.field = NaturalSortField(for_field="test_field")

  @mock.patch(FIELDS_MODULE + ".NaturalSortField.naturalize")
  def test_presave(self, m_naturalize):

    mock_model = mock.Mock()
    mock_model.test_field = "The unnaturalized string"
    m_naturalize.return_value = "mocked naturalized string"

    result = self.field.pre_save(mock_model, None)

    self.assertEqual(result, m_naturalize.return_value)

    m_naturalize.assert_called_once_with(mock_model.test_field,)

  @mock.patch(FIELDS_MODULE + ".models.CharField.deconstruct")
  def test_deconstruct(self, m_deconstruct):

    m_deconstruct.return_value = (
        "mock_name",
        "mock_path",
        ['argument!'],
        {},
    )

    name, path, args, kwargs = self.field.deconstruct()

    self.assertEqual(name, "mock_name")
    self.assertEqual(path, "mock_path")
    self.assertListEqual(args, ['argument!', "test_field"])
    self.assertDictEqual(kwargs, {})


class TestNaturalSortFieldNaturalize(TestCase):
  """Test the NaturalSortField naturalize method."""

  def setUp(self):
    self.field = NaturalSortField(for_field="non-existent")

  def test_is_lowercase(self):
    test_value = "UPPER_CASE"

    result = self.field.naturalize(test_value)
    self.assertEqual(result, test_value.lower())

  def test_strips_white_space(self):
    test_value = " string with white space "

    result = self.field.naturalize(test_value)
    self.assertEqual(result, test_value.strip())

  def test_removes_preceding_the(self):
    test_value = "The extremely useless thing."

    result = self.field.naturalize(test_value)
    self.assertEqual(result, test_value[4:])

  def test_truncates_to_max_length(self):
    test_value = "something" * 100

    result = self.field.naturalize(test_value)
    self.assertEqual(
        len(result),
        self.field.max_length,
    )

  def test_naturalizes_integers(self):
    test_value = "0004"

    result = self.field.naturalize(test_value)
    self.assertEqual(
        result,
        '%08d' % int(test_value),
    )

  def test_naturalizes_multiple_integers(self):
    test_value = "0004-0003"
    values = test_value.split("-")

    result = self.field.naturalize(test_value)
    self.assertEqual(
        result,
        '%08d-%08d' % (int(values[0]), int(values[1])),
    )
