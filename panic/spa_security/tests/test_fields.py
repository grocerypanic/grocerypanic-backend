"""Test the customized bleach field"""

from django.test import TestCase, override_settings

from ..fields import BlondeCharField


class BleachFieldTest(TestCase):
  """Test the custom bleach field"""

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
