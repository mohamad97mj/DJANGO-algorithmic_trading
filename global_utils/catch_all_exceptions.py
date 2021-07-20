import functools
import traceback
from global_utils.my_logging import my_get_logger


def catch_all_exceptions(log_level='error', reraise=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = my_get_logger()
                log_level_mapper = {
                    'warning': logger.warning,
                    'error': logger.error,
                }
                log_level_mapper[log_level](
                    "func={} args={} kwargs={} message={} traceback={}".format(func,
                                                                               args,
                                                                               kwargs,
                                                                               e,
                                                                               traceback.format_exc()))
                if reraise:
                    raise e

        return wrapper

    return decorator
