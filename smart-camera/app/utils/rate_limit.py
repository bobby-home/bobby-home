import threading
import time
from functools import wraps


def rate_limited(max_per_second: float, thread_safe: bool = True, block: bool = True):
    """
    Rate-limits the decorated function locally, for one process.

    Parameters
    ----------
    max_per_second : float
        The maximum number of times that the wrapped function can be called per seconds.
    thread_safe : bool
        If set to True, the function uses a Lock to exclusively use the `perf_counter`,
        as the name suggests, use it if you use this function with multiple threads.
    block : bool
        If set to True, the function block the thread until the function can be called (according to the rate limit).
        Otherwise, it returns None without blocking and without calling the function.
    -------

    """
    if max_per_second == 0:
        raise ValueError(f'max_per_second cannot be 0')

    if thread_safe:
        lock = threading.Lock()

    min_interval = 1.0 / max_per_second

    def decorate(func):
        last_time_called = None

        @wraps(func)
        def rate_limited_function(*args, **kwargs):
            if thread_safe:
                lock.acquire()

            nonlocal last_time_called
            try:
                if last_time_called is not None:
                    elapsed = time.time() - last_time_called
                    left_to_wait = min_interval - elapsed
                else:
                    left_to_wait = 0

                if left_to_wait > 0:
                    if block is True:
                        time.sleep(left_to_wait)
                    else:
                        return None

                last_time_called = time.time()
                return func(*args, **kwargs)
            finally:
                if thread_safe:
                    lock.release()

        return rate_limited_function

    return decorate
