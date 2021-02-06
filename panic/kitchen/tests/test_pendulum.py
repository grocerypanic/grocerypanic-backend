"""Test the pendulum is correctly configured for Sunday start weeks."""

import pendulum
from django.test import TestCase


class TestWeekConfiguration(TestCase):

  def test_start_of_week(self):
    assert pendulum.now().start_of('week').day_of_week == pendulum.SUNDAY

  def test_end_of_week(self):
    assert pendulum.now().end_of('week').day_of_week == pendulum.SATURDAY
