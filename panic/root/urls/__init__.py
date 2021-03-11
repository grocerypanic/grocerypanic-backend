"""URL configuration for the Panic application."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('appengine.urls')),
    path('', include('root.urls.api.v1')),
    path('watchman/', include('watchman.urls')),
]

if settings.ENVIRONMENT in ['local', 'stage', 'admin']:
  urlpatterns = [path('admin/', admin.site.urls)] + urlpatterns
  urlpatterns += [path('', include('root.urls.openapi'))]
