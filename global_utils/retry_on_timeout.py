import functools
import traceback
import time
from global_utils.my_logging import my_get_logger


def retry_on_timout(timeout_error=Exception, attempts=None, delay=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def caught_func():
                try:
                    _result, _error = func(*args, **kwargs), False
                except timeout_error as e:
                    logger = my_get_logger()
                    logger.debug('retry on timeout!')
                    logger.warning(
                        "func={} args={} kwargs={} message={} traceback={}".format(func,
                                                                                   args,
                                                                                   kwargs,
                                                                                   e,

                                                                                   traceback.format_exc()))
                    _result, _error = None, True
                    time.sleep(delay)
                finally:
                    return _result, _error

            if attempts:
                for _ in range(attempts):
                    result, error = caught_func()
                    if not error:
                        return result

            else:
                while True:
                    result, error = caught_func()
                    if not error:
                        return result

        return wrapper

    return decorator
