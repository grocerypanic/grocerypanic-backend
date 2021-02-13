"""Urls for the appengine app."""

from django.conf.urls import url

from .views import WarmUp

urlpatterns = [
    url('^_ah/warmup/?$', WarmUp.as_view(), name='appengine_warmup'),
]
