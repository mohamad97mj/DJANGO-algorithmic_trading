import os
from .main import STATIC_ROOT, DEBUG
import logging.config
from pathlib import Path

LOGGING_CONFIG = None

LOG_DIR = os.path.join(STATIC_ROOT, 'logs')

PYTHON_LOGGING_FORMAT = '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
DJANGO_LOGGING_FORMAT = '{levelname} {asctime} {module} {process:d} {thread:d} {message}'

DEFAULT_LOG_LEVEL = 'INFO' if DEBUG else 'INFO'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': DJANGO_LOGGING_FORMAT,
            'datefmt': "%d/%b/%Y %H:%M:%S",
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': DEFAULT_LOG_LEVEL,
            'propagate': True,
        },
        'django.server': {
            'handlers': ['console'],
            'level': DEFAULT_LOG_LEVEL,
            'propagate': False,
        },
        'trader': {
            'handlers': [
                'console',
            ],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

logging.config.dictConfig(LOGGING)
