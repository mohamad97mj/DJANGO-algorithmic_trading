import logging
import pytz
import os
from datetime import datetime
from django.conf import settings
from pathlib import Path

symbol2level = {
    'd': logging.DEBUG,
    'i': logging.INFO,
    'w': logging.WARNING,
    'e': logging.ERROR,
    'c': logging.CRITICAL,
}


class LevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        return record.levelname.lower() == self.level


def my_get_logger(logger_name='videoserver.video_api'):
    logger_name = logger_name
    logger = logging.getLogger(logger_name)
    if settings.DEBUG:
        load_file_handlers(logger)

    return logger


def load_file_handlers(logger):
    now = datetime.now(pytz.timezone(settings.TIME_ZONE))
    handler_name_prefix = now.strftime('%Y%m%d%H')
    parent2_dir_name = now.strftime('%Y-%m-%d')
    parent2_dir_path = os.path.join(settings.LOG_DIR, parent2_dir_name)

    for handler in logger.handlers:
        if handler.name.startswith(handler_name_prefix):
            break
    else:
        for symbol, level in symbol2level.items():
            level_name = logging.getLevelName(level).lower()
            parent_dir_name = level_name
            parent_dir_path = os.path.join(parent2_dir_path, parent_dir_name)
            Path(parent_dir_path).mkdir(parents=True, exist_ok=True)
            file_name = '{}.txt'.format(str(now.hour))
            fh = logging.FileHandler(os.path.join(parent_dir_path, file_name))
            fh.name = handler_name_prefix + symbol
            fh.setLevel(level)
            fh.addFilter(LevelFilter(level=level_name))
            formatter = logging.Formatter(settings.PYTHON_LOGGING_FORMAT)
            fh.setFormatter(formatter)
            logger.addHandler(fh)
