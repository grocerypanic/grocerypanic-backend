"""Url Patterns for the Social Accounts App"""

from django.urls import path

from .views import FacebookConnect, FacebookLogin, GoogleConnect, GoogleLogin

app_name = "social_accounts"

urlpatterns = [
    path("facebook/", FacebookLogin.as_view(), name='fb_login'),
    path("google/", GoogleLogin.as_view(), name='google_login'),
    path("connect/facebook/", FacebookConnect.as_view(), name='fb_connect'),
    path("connect/google/", GoogleConnect.as_view(), name='google_connect'),
]
