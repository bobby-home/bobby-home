import threading
import time
from functools import wraps


def rate_limited(max_per_second: int, thread_safe=True):
    """Rate-limits the decorated function locally, for one process."""
    if thread_safe:
        lock = threading.Lock()

    min_interval = 1.0 / max_per_second

    def decorate(func):
        last_time_called = time.perf_counter()

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            if thread_safe:
                lock.acquire()

            nonlocal last_time_called
            try:
                elapsed = time.perf_counter() - last_time_called
                left_to_wait = min_interval - elapsed

                if left_to_wait > 0:
                    time.sleep(left_to_wait)

                return func(*args, **kwargs)
            finally:
                last_time_called = time.perf_counter()

                if thread_safe:
                    lock.release()

        return rate_limited_function

    return decorate
