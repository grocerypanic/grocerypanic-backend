"""Panic `admin` environment settings."""

from corsheaders.defaults import default_headers
from django.contrib.messages import constants as message_constants

ALLOWED_HOSTS = ['*']
DEBUG = True
DEBUG_PROPAGATE_EXCEPTIONS = True

CUSTOM_MIDDLEWARE = []
CUSTOM_INSTALLED_APPS = []

STATIC_URL = '/static/'

CURRENT_PROTOCOL = 'http'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "http"

MESSAGE_LEVEL = message_constants.WARNING

JWT_AUTH_COOKIE = 'panic_auth_prod'
CSRF_COOKIE_NAME = "panic_csrf_prod"

CORS_ALLOW_HEADERS = default_headers + ('Access-Control-Allow-Origin',)

DEFAULT_FROM_EMAIL = "no-reply@grocerypanic.com"
