"""Fixtures related to the Django framework."""

import datetime

import pytz


class MockRequest:
  """Test double for a request object."""

  def __init__(self, user):
    self.user = user


def deserialize_datetime(string):
  """Convert a serialized datetime into a python datetime object."""

  return pytz.utc.localize(
      datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
  )


def deserialize_date(string):
  """Convert a serialized date into a python datetime object."""
  return datetime.datetime.strptime(string, "%Y-%m-%d").date()
