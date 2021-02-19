"""Test the custom user details serializer."""

from django.contrib.auth import get_user_model

from ...tests.fixtures.django import MockRequest
from ...tests.fixtures.serializers import SerializerTestHarness
from ..details import UserDetailsSerializer


class SerializeTransformations:

  @staticmethod
  def email(_):
    return None

  @staticmethod
  def password(_):
    return None


class DeserializeTransformations:

  @staticmethod
  def timezone(value):
    return str(value)


# pylint: disable=too-many-instance-attributes
class DetailsSerializerTest(SerializerTestHarness):
  __test__ = True
  serializer = UserDetailsSerializer
  model = get_user_model()

  def create_data_hook(self):
    self.fields = {"language_code": 20}
    self.deserializer_data = {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "unbelievable",
        "timezone": "America/Toronto",
        "language_code": "fr",
    }
    self.request = MockRequest()
    self.context = {'request': self.request}
    self.serializer_operations = SerializeTransformations()
    self.deserializer_operations = DeserializeTransformations()
    self.serializer_data = {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "unbelievable",
        "timezone": "America/Toronto",
        "language_code": "fr",
        "has_profile_initialized": True,
    }
    self.serializer_data_field = "username"

    self.serializer_data_invalid = [{
        "username": "testuser1",
        "email": "test@example.com",
        "password": "unbelievable",
        "timezone": "not a timezone",
    }, {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "unbelievable",
        "language_code": "not a language code",
    }, {
        "username": "testuser1",
        "email": "test@example.com",
        "password": "unbelievable",
        "timezone": "not a timezone",
        "language_code": "not a language code",
    }]
