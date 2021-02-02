"""Pagination for Kitchen Models"""

from django.conf import settings
from rest_framework.pagination import PageNumberPagination


class PagePagination(PageNumberPagination):
  page_size = settings.PAGE_SIZE
  max_page_size = settings.PAGE_SIZE_MAX
  page_size_query_param = settings.PAGE_SIZE_PARAM
  page_query_param = settings.PAGE_QUERY_PARAM


class LegacyTransactionPagination(PagePagination):
  page_size = settings.LEGACY_TRANSACTION_HISTORY_UPPER_BOUND


class PagePaginationWithOverride(PagePagination):
  """Adds Page Pagination with an override feature."""

  def paginate_queryset(self, queryset, request, view=None):
    """
    Overrides the base method for paginate_queryset and adds a conditional
    to allow bypassing pagination.

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
