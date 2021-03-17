"""Test the ItemActivityReport API."""

import pytz
from django.test import TestCase
from django.urls import reverse
from django.utils.http import urlencode
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient

from ...serializers.reports.item_activity import ItemActivityReportSerializer
from .fixtures.fixtures_item_activity import ItemActivityViewSetHarness

ACTIVITY_REPORT_VIEW = "v1:item-activity-detail"


def item_pk_url(item):
  return reverse(ACTIVITY_REPORT_VIEW, args=[item])


# pylint: disable=dangerous-default-value
def item_query_url(item, query_kwargs={}):
  return '{}?{}'.format(item_pk_url(item), urlencode(query_kwargs))


class PublicItemActivityViewSetTest(TestCase):
  """Test the public ItemActivityReport API."""

  def setUp(self):
    self.client = APIClient()

  def test_get_login_required(self):
    res = self.client.get(item_pk_url(0))

    self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


@freeze_time("2020-01-14")
class PrivateItemActivityViewSetTest(ItemActivityViewSetHarness):
  """Test the authorized ItemActivityReport API."""

  def setUp(self):
    super().setUp()
    self.user1.timezone = self.timezone
    self.user1.save()

    self.client = APIClient()
    self.client.force_authenticate(self.user1)

  def _user_date(self, datetime_object):
    return datetime_object.astimezone(pytz.timezone(self.timezone)).date()

  def test_activity_first(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['activity_first'],
        self.initial_transaction_date,
    )

  def test_usage_total(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['usage_total'], self.item1.usage_total)

  def test_usage_avg_week(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['usage_avg_week'], self.item1.usage_avg_week)

  def usage_avg_month(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(res.data['usage_avg_month'], self.item1.usage_avg_month)

  def test_recent_user_timezone_utc(self):
    res = self.client.get(item_pk_url(self.item1.id))
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    self.assertEqual(
        res.data['recent_activity']['user_timezone'],
        str(self.user1.timezone),
    )

  def test_recent_user_timezone_alternate(self):
    test_timezone = "Asia/Hong_Kong"
    self.user1.timezone = test_timezone
    self.user1.save()

    res = self.client.get(item_pk_url(self.item1.id))
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    self.assertEqual(
        res.data['recent_activity']['user_timezone'],
        str(self.user1.timezone),
    )

  def test_recent_activity_last_two_weeks_utc(self):
    res = self.client.get(item_pk_url(self.item1.id))
    serializer = ItemActivityReportSerializer(
        self.item1,
        context={
            'request': self.MockRequest,
        },
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['recent_activity']['activity_last_two_weeks'],
        serializer.data['recent_activity']['activity_last_two_weeks'],
    )

  def test_recent_activity_last_two_weeks_ordering(self):
    res = self.client.get(item_pk_url(self.item1.id))
    self.assertEqual(res.status_code, status.HTTP_200_OK)

    consumption_past_two_weeks = (
        res.data['recent_activity']['activity_last_two_weeks']
    )

    assert len(consumption_past_two_weeks) == 14

    self.assertEqual(
        self.deserialize_date(consumption_past_two_weeks[0]['date']),
        self._user_date(self.today)
    )
    self.assertEqual(
        self.deserialize_date(consumption_past_two_weeks[5]['date']),
        self._user_date(self.five_days_ago)
    )

  def test_recent_usage_current_week(self):
    res = self.client.get(item_pk_url(self.item1.id))
    serializer = ItemActivityReportSerializer(
        self.item1,
        context={
            'request': self.MockRequest,
        },
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['recent_activity']['usage_current_week'],
        serializer.data['recent_activity']['usage_current_week']
    )

  def test_recent_usage_current_month(self):
    res = self.client.get(item_pk_url(self.item1.id))
    serializer = ItemActivityReportSerializer(
        self.item1,
        context={
            'request': self.MockRequest,
        },
    )

    self.assertEqual(res.status_code, status.HTTP_200_OK)
    self.assertEqual(
        res.data['recent_activity']['usage_current_month'],
        serializer.data['recent_activity']['usage_current_month']
    )


@freeze_time("2020-01-14")
class PrivateItemActivityViewSetAnotherUserTest(ItemActivityViewSetHarness):
  """Test the authorized ItemActivityReport API as another user."""

  @classmethod
  def create_data_hook(cls):
    super().create_data_hook()
    test_data2 = cls.create_dependencies(2)
    cls.user2 = test_data2['user']

  def setUp(self):
    super().setUp()
    self.client = APIClient()
    self.client.force_authenticate(self.user2)

  def test_get_item_history(self):
    res = self.client.get(item_pk_url(self.item1.id))

    self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
