"""Timezone utilities."""

import pytz


def generate_timezones():
  """Generate a list of Timezones for use by the client application."""

  timezones = pytz.common_timezones

  for index, timezone in enumerate(timezones):
    yield {"id": index, "name": timezone}
