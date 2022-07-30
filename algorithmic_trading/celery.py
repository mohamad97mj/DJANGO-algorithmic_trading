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
    'run-every-hour': {
        'task': 'futures_trader.tasks.technical_auto_trade',
        'schedule': crontab(minute=54),
        'options': {
            'expires': 30.0,
        },
    },
}
