"""Fixtures related to urlpatterns."""

from unittest.mock import Mock

from django.urls import path

urlpatterns = [
    path('/test/1', Mock(), name="test1"),
    path('/test/2', Mock(), name="test2"),
    path('/test/3', Mock(), name="test3"),
]
