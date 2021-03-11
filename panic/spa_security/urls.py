"""URLs for the spa_security app."""

from django.urls import path

from spa_security.views.csrf_token import CSRFTokenView

app_name = "spa_security"

urlpatterns = [
    path("csrf/", CSRFTokenView.as_view(), name='csrf'),
]
