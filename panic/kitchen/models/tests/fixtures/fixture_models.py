"""Model Test Fixtures."""

from django.core.exceptions import ValidationError


def generate_base(base):
  """Create a model test harness class inheriting from the specified base.

  :param base: A base class (usually a test harness) to use
  :type base: class

  :return: A test class derived from the specified base
  :rtype: class
  """

  class ModelTestBase(base):
    """Common base class for model testing."""

    data: dict
    fields: dict

    @staticmethod
    def generate_overload(fields):
      return_value = []
      for key, value in fields.items():
        return_value.append({key: "abc" * value})
      return return_value

    def test_field_lengths(self):
      for overloaded_field in self.generate_overload(self.fields):
        local_data = dict(self.data)
        local_data.update(overloaded_field)
        with self.assertRaises(ValidationError):
          _ = self.create_test_instance(**local_data)

  return ModelTestBase
