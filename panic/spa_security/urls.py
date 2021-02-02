"""Security App Urls"""

from django.urls import path

from spa_security.views import CSRFView

app_name = "spa_security"

urlpatterns = [
    path("csrf/", CSRFView.as_view(), name='csrf'),
]
