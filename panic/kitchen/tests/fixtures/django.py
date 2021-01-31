"""Fixtures Related to the Django Framework"""

import datetime

import pytz


class MockRequest:

  def __init__(self, user):
    self.user = user


def deserialize_datetime(string):
  return pytz.utc.localize(
      datetime.datetime.strptime(string, "%Y-%m-%dT%H:%M:%SZ")
  )
