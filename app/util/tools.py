from functools import wraps
import time
import logging


# check time consumption of a function
def warn(timeout):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            used = time.time() - start
            if used > timeout:
                msg = '"%s:%s > %s"' % (func.__name__, used, timeout)
                logging.warning(msg=msg)
            return res

        return wrapper

    return decorator


from random import randint


@warn(1.5)
def test():
    print('I am in test!')
    while randint(0, 1):
        time.sleep(0.5)


if __name__ == "__main__":
    for v in range(30):
        test()
