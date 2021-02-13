"""Panic database settings per environments."""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES_CONFIGURATIONS = {
    'remote': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("POSTGRES_DB"),
        'USER': os.environ.get("POSTGRES_USER"),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD"),
        'HOST': os.environ.get("POSTGRES_HOSTNAME"),
    },
    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

DATABASES_AVAILABLE = {
    'test': DATABASES_CONFIGURATIONS['remote'],
    'local': DATABASES_CONFIGURATIONS['remote'],
    'stage': DATABASES_CONFIGURATIONS['remote'],
    'prod': DATABASES_CONFIGURATIONS['remote'],
    'admin': DATABASES_CONFIGURATIONS['remote'],
}
