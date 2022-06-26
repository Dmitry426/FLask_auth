import os

log_path = os.path.join("/", "src/logs/auth_api.json")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {'json': {'()': 'ecs_logging.StdlibFormatter', }, },
    'handlers': {
        'auth_api': {
            'level': 'INFO',
            'formatter': 'json',
            'class': 'logging.FileHandler',
            'filename': log_path,
        },
        'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', },
    },
    'loggers': {
        '': {'handlers': ['console'], 'level': 'INFO', },
        'auth_api': {'handlers': ['auth_api'], 'level': 'INFO', 'propagate': False, },
    },
    'root': {'level': 'INFO', 'handlers': ['console', ], },
}
