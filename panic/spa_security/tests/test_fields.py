"""Test the custom model field."""

from django.test import SimpleTestCase, override_settings

from ..fields import BlondeCharField


class BlondeCharFieldTest(SimpleTestCase):
  """Test the BlondeCharField class."""

  def setUp(self):

    class EmptyObject:
      field_name = "Initial&Value"

    self.field = BlondeCharField()
    self.field.attname = "field_name"
    self.object = EmptyObject()

  @override_settings(BLEACH_RESTORE_LIST={})
  def test_normal_execution(self):
    self.field.pre_save(self.object, "")
    self.assertEqual(self.object.field_name, "Initial&amp;Value")

  @override_settings(BLEACH_RESTORE_LIST={"&amp;": "&"})
  def test_override_execution(self):
    self.field.pre_save(self.object, "")
    self.assertEqual(self.object.field_name, "Initial&Value")
