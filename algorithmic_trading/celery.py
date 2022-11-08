import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'algorithmic_trading.settings')

app = Celery('algorithmic_trading')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'auto-trade': {
        'task': 'forex_trader.tasks.generate_technical_signals',
        'schedule': crontab(minute=30),
        'options': {
            'expires': 30.0,
        },
    },
    # 'cancel-orders': {
    #     'task': 'futures_trader.tasks.cancel_remaining_orders',
    #     'schedule': crontab(),
    #     'options': {
    #         'expires': 30.0,
    #     },
    # }
}
