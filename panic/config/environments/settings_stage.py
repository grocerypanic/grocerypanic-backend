"""Panic `stage` environment configuration."""

import os

from corsheaders.defaults import default_headers
from django.contrib.messages import constants as message_constants

ALLOWED_HOSTS = ['*']
DEBUG = False
DEBUG_PROPAGATE_EXCEPTIONS = True
STATICFILES_STORAGE = \
    'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

CUSTOM_MIDDLEWARE = []
CUSTOM_INSTALLED_APPS = []

CURRENT_DOMAIN = os.environ.get("STAGE_HOSTNAME", None)
CURRENT_PROTOCOL = 'https'
ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

REST_COOKIES_SECURE = True
JWT_AUTH_COOKIE_SAMESITE = "Strict"
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SAMESITE = "Strict"
CSRF_COOKIE_SECURE = True

CSRF_TRUSTED_ORIGINS = ['stage.grocerypanic.com', 'demo.grocerypanic.com']
JWT_AUTH_COOKIE = 'panic_auth_stage'
CSRF_COOKIE_NAME = "panic_csrf_stage"

DEFAULT_FROM_EMAIL = "no-reply@grocerypanic.com"

MESSAGE_LEVEL = message_constants.WARNING

CORS_ALLOW_HEADERS = default_headers + ('Access-Control-Allow-Origin',)
