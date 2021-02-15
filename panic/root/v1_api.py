"""Root v1 API URLs."""

from dj_rest_auth.registration.views import ConfirmEmailView, VerifyEmailView
from dj_rest_auth.views import PasswordResetConfirmView
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
        'api/v1/auth/password/reset/confirm/<slug:uidb64>/<slug:token>/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        "api/v1/auth/",
        include('dj_rest_auth.urls'),
    ),
    path(
        'api/v1/auth/registration/account-confirm-email/<str:key>/',
        ConfirmEmailView.as_view(),
    ),
    path(
        "api/v1/auth/registration/",
        include('dj_rest_auth.registration.urls'),
    ),
    path(
        'api/v1/auth/registration/account-confirm-email/',
        VerifyEmailView.as_view(),
        name='account_email_verification_sent',
    ),
    path(
        "api/v1/auth/social/",
        include("social_accounts.urls"),
    ),
]
