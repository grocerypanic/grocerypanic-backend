"""Aggregated Models"""

import pendulum

from . import inventory, item, shelf, store, suggested, transaction

pendulum.week_starts_at(pendulum.SUNDAY)
pendulum.week_ends_at(pendulum.SATURDAY)
