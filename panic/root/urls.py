"""panic URL Configuration"""

from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from .v1_api import v1_urlpatterns

urlpatterns = [
    path("", include("appengine.urls")),
    path('watchman/', include("watchman.urls")),
]

urlpatterns += v1_urlpatterns

if settings.ENVIRONMENT in ['local', 'stage', 'admin']:
  urlpatterns = [path('admin/', admin.site.urls)] + urlpatterns

  SchemaView = get_schema_view(
      openapi.Info(
          title="Don't Panic API!",
          default_version='v1',
          description="A Pandemic Kitchen Inventory Manager",
          terms_of_service="https://www.google.com/policies/terms/",
          contact=openapi.Contact(email="niall@niallbyrne.ca"),
          license=openapi.License(name="MPL 2.0 License"),
      ),
      public=True,
      permission_classes=(permissions.AllowAny,),
  )

  urlpatterns += [
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
