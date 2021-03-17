"""URLs for the legal app."""

from django.urls import path

from .views import PrivacyPolicyView, TOSView

urlpatterns = [
    path(
        'legal/tos/',
        TOSView.as_view(),
        name='legal_tos',
    ),
    path(
        'legal/privacy/',
        PrivacyPolicyView.as_view(),
        name='legal_privacypolicy',
    ),
]
