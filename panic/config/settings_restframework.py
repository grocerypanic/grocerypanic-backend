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
        ]
    },
    'stage': {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'spa_security.auth_cookie.JWTCookieAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle'
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '5/minute',
            'user': '15/minute'
        }
    },
}