"""URL configuration for the OpenAPI documentation endpoints."""

from django.conf.urls import url
from django.urls import reverse_lazy
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

SchemaView = get_schema_view(
    openapi.Info(
        title="Don't Panic API!",
        default_version='v1',
        description="A Pandemic Kitchen Inventory Manager",
        terms_of_service=reverse_lazy('legal_tos'),
        contact=openapi.Contact(email="niall@niallbyrne.ca"),
        license=openapi.License(name="MPL 2.0 License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(
        r'^swagger(?P<format>\.json|\.yaml)$',
        SchemaView.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    url(
        r'^swagger/$',
        SchemaView.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
]
