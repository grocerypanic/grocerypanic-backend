"""Throttling Settings"""

REST_FRAMEWORK_AVAILABLE = {
    'test': {},
    'local': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'spa_security.auth_cookie.JWTCookieAuthentication',
            'rest_framework.authentication.BasicAuthentication',
            'rest_framework.authentication.TokenAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
            'kitchen.permissions.IsOwner',
        ],
        'DEFAULT_FILTER_BACKENDS':
            ('django_filters.rest_framework.DjangoFilterBackend',),
    },
    'stage': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'spa_security.auth_cookie.JWTCookieAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
            'kitchen.permissions.IsOwner',
        ],
        'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle'
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '5/minute',
            'user': '120/minute'
        },
        'DEFAULT_FILTER_BACKENDS':
            ('django_filters.rest_framework.DjangoFilterBackend',),
    },
    'prod': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'spa_security.auth_cookie.JWTCookieAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
            'kitchen.permissions.IsOwner',
        ],
        'DEFAULT_RENDERER_CLASSES': ('rest_framework.renderers.JSONRenderer',),
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle'
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '5/minute',
            'user': '120/minute'
        },
        'DEFAULT_FILTER_BACKENDS':
            ('django_filters.rest_framework.DjangoFilterBackend',),
    },
    'admin': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'spa_security.auth_cookie.JWTCookieAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_FILTER_BACKENDS':
            ('django_filters.rest_framework.DjangoFilterBackend',),
    },
}
