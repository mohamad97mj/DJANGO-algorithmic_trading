import sys
import os
import functools
import logging

logging.basicConfig(level=logging.INFO)


def log(_func=None):
    def log_info(func):
        @functools.wraps(func)
        def log_wrapper(*args, **kwargs):

            """log function begining"""
            # logging.info("Begin function {}".format(func.__name__))
            print('--Begin function {} - args:{}, kwargs:{}'.format(func.__name__, args, kwargs))
            try:
                """ log return value from the function """
                value = func(*args, **kwargs)
                # logging.info(f"Returned: - End function {value!r}")
                print('--End function {} - returned value: '.format(func.__name__, value))
            except:
                """log exception if occurs in function"""
                logging.error(f"--Exception: {str(sys.exc_info()[1])}")
                raise
            return value

        return log_wrapper

    if _func is None:
        return log_info
    else:
        return log_info(_func)
