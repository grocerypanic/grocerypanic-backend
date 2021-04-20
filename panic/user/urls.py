"""URLs for the user app."""

from django.urls import path

from .views import TimeZones

app_name = "user"

urlpatterns = [
    path("timezones/", TimeZones.as_view(), name='timezones'),
]
