"""Panic email configuration."""

import os

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_PORT = os.environ.get('DJANGO_EMAIL_PORT')
EMAIL_HOST = os.environ.get('DJANGO_EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('DJANGO_EMAIL_HOST_PASSWORD')
