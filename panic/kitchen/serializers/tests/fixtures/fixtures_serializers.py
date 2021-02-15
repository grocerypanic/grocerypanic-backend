"""Serializer Test Fixtures."""

from rest_framework import serializers


def generate_base(base):
  """Create a serializer test harness class inheriting from the specified base.

  :param base: A base class (usually a test harness) to use
  :type base: class

  :return: A test class derived from the specified base
  :rtype: class
  """

  class SerializerTestHarness(base):
    """Test harness class for serializer testing."""

    data: dict
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
        local_data = dict(self.data)
        local_data.update(overload)
        with self.assertRaises(serializers.ValidationError):
          serialized = self.serializer(
              context={'request': self.request},
              data=local_data,
          )
          serialized.is_valid(raise_exception=True)

  return SerializerTestHarness
