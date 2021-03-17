"""Fixtures for working with freezegun fakedates and datetimes."""

from datetime import datetime, timedelta


def to_realdate(queryset, field, offset=0):
  """Convert a QuerySet with a field containing a datetime, to a python date.
  This can be used inside a class or function where freezegun is active.

  This is intended to make comparing QuerySets with dates easier.

  :param queryset: A django QuerySet object, or a list
  :type queryset: :class:`django.db.models.QuerySet`, list
  :param field: The field containing the datetime object.
  :type field: str
  :param offset: An optional integer representing a time offset in days
  :type offset: int

  :returns: The queryset with modified values
  :rtype: :class:`django.db.models.QuerySet`, list
  """
  for record in queryset:
    date_object = record[field]
    if offset:
      days = timedelta(days=offset)
      date_object = (date_object - days)

    record[field] = datetime.fromtimestamp(date_object.timestamp()).date()
  return queryset
