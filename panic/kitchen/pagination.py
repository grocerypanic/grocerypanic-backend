"""Pagination for the kitchen app."""

from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class BasePagePagination(PageNumberPagination):
  """Base page pagination."""

  page_size = settings.PAGE_SIZE
  max_page_size = settings.PAGE_SIZE_MAX
  page_size_query_param = settings.PAGE_SIZE_PARAM
  page_query_param = settings.PAGE_QUERY_PARAM


class LegacyTransactionPagination(BasePagePagination):
  """Pagination for the deprecated transaction list endpoint."""

  page_size = settings.LEGACY_TRANSACTION_HISTORY_UPPER_BOUND


class PagePaginationWithOverride(BasePagePagination):
  """Adds page pagination with an override feature."""

  def paginate_queryset(self, queryset, request, view=None):
    """Add a conditional to allow bypassing pagination on the base method.

    :param queryset: A django queryset to paginate
    :type queryset: :class:`django.db.models.query.QuerySet`
    :param request: The request being made
    :type request: :class:`django.http.request.Request`
    :param view: The view being paginated
    :type view: function

    :returns: The paginated query set or None
    :rtype: None, :class:`django.db.models.query.QuerySet`
    """
    if request.query_params.get(settings.PAGINATION_OVERRIDE_PARAM):
      return None

    return super().paginate_queryset(queryset, request, view)
