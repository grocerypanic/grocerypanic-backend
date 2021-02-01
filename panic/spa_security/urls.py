"""Security App Urls"""

from django.urls import include, path

from spa_security.views import CSRFview

app_name = "spa_security"

csrf_url = [
    path("csrf/", CSRFview.as_view(), name='csrf'),
]

urlpatterns = [
    path('', include(csrf_url)),
]
