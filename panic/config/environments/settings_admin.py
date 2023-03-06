"""Panic `admin` environment settings."""

from corsheaders.defaults import default_headers
from django.contrib.messages import constants as message_constants

ALLOWED_HOSTS = ['*']
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

CUSTOM_MIDDLEWARE = []
CUSTOM_INSTALLED_APPS = []

CURRENT_DOMAIN = "localhost"
CURRENT_PROTOCOL = 'http'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE_SAMESITE": "lax",
    "JWT_AUTH_COOKIE": "panic_auth_prod",
    "JWT_AUTH_REFRESH_COOKIE": "panic_refresh_prod",
    "JWT_AUTH_SECURE": False,
    "JWT_AUTH_HTTPONLY": False,
    "USER_DETAILS_SERIALIZER": "user.serializers.details.UserDetailsSerializer",
}

CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = False

CSRF_TRUSTED_ORIGINS = ['localhost', '127.0.0.1']
CSRF_COOKIE_NAME = "panic_csrf_prod"

DEFAULT_FROM_EMAIL = "no-reply@grocerypanic.com"

MESSAGE_LEVEL = message_constants.WARNING

CORS_ALLOW_HEADERS = default_headers + ('Access-Control-Allow-Origin',)
