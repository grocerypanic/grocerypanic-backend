"""Test the timezone utilities."""

import pytz
from django.test import TestCase

from ..timezones import generate_timezones


class TestGenerateTimezones(TestCase):
  """Test the generate_timezones function."""

  def test_timezone_list(self):
    timezones = list(pytz.common_timezones)
    timezones.sort()

    for index, generated in enumerate(generate_timezones()):
      self.assertEqual(
          {
              "id": index,
              "name": timezones[index]
          },
          generated,
      )
