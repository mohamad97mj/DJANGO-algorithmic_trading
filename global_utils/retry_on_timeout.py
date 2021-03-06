import functools
import traceback
import time
from global_utils.my_logging import my_get_logger


def retry_on_timeout(timeout_errors=None, attempts=None, delay=5):
    timeout_errors = timeout_errors or Exception

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            def caught_func():
                _result, _error, _none_timeout_error = None, True, False
                logger = my_get_logger()
                try:
                    _result, _error = func(*args, **kwargs), False
                except timeout_errors as e:
                    logger.warning('retry on timeout: {}!'.format(func.__name__))
                    # logger.warning(
                    #     "func={} args={} kwargs={} message={} traceback={}".format(func,
                    #                                                                args,
                    #                                                                kwargs,
                    #                                                                e,
                    #                                                                traceback.format_exc()))
                    time.sleep(delay)
                except Exception as e:
                    _none_timeout_error = True
                    logger.exception(e)
                finally:
                    return _result, _error, _none_timeout_error

            if attempts:
                for _ in range(attempts):
                    result, error, none_timeout_error = caught_func()
                    if none_timeout_error:
                        break
                    if not error:
                        return result
            else:
                while True:
                    result, error, none_timeout_error = caught_func()
                    if none_timeout_error:
                        break
                    if not error:
                        return result

        return wrapper

    return decorator


def async_retry_on_timeout(public_client, timeout_errors=None, attempts=None, delay=5):
    timeout_errors = timeout_errors or Exception

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            async def caught_func():
                _result, _error = None, True
                logger = my_get_logger()
                try:
                    while not public_client.fetch_status()['status'] == 'ok':
                        logger.warning('Exchange status is not ok!')
                        time.sleep(2)
                    _result, _error = await func(*args, **kwargs), False

                except timeout_errors as e:
                    logger.warning('Retry on timeout: {}!'.format(func.__name__))
                    # logger.warning(
                    #     "func={} args={} kwargs={} message={} traceback={}".format(func,
                    #                                                                args,
                    #                                                                kwargs,
                    #                                                                e,
                    #
                    #                                                                traceback.format_exc()))
                    _result, _error = None, True
                    time.sleep(delay)
                except Exception as e:
                    logger.exception(e)
                finally:
                    return _result, _error

            if attempts:
                for _ in range(attempts):
                    result, error = await caught_func()
                    if not error:
                        return result

            else:
                while True:
                    result, error = await caught_func()
                    if not error:
                        return result

        return wrapper

    return decorator
