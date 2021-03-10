"""Serializer field for the PreferredStore M2M through model."""

from drf_yasg import openapi

from ..store import Store
from .m2m import M2MThroughSerializerField


class PreferredStoreSerializerField(M2MThroughSerializerField):
  """Serializer field for the PreferredStore M2M through model."""

  def __init__(self, **kwargs):
    kwargs['queryset'] = Store.objects.all()
    super().__init__(**kwargs)

  class Meta:
    ref_name = "Store"
    swagger_schema_fields = {
        "title": "Store",
        "type": openapi.TYPE_INTEGER,
    }
