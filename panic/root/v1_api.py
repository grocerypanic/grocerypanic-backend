"""Root V1 API Urls"""

from allauth.socialaccount.views import connections, signup
from django.urls import include, path

v1_urlpatterns = [
    path(
        "api/",
        include(
            "kitchen.versions.v1",
            namespace="v1",
        ),
    ),
    path(
        "api/v1/auth/",
        include("spa_security.urls"),
    ),
    path(
        "api/v1/auth/",
        include('dj_rest_auth.urls'),
    ),
    path(
        "api/v1/auth/registration/",
        include('dj_rest_auth.registration.urls'),
    ),
    path(
        "api/v1/auth/social/",
        include("social_accounts.urls"),
    ),
    path(
        "api/v1/auth/social/signup/",
        signup,
        name='socialaccount_signup',
    ),
    path(
        "api/v1/auth/social/connect/",
        connections,
        name='socialaccount_connections',
    ),
]
