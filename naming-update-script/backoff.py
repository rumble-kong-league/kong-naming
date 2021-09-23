import random, time


def retry_with_backoff(retries=5, backoff_in_seconds=1, logger=None):
    def rwb(f):
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return f(*args, **kwargs)
                except:
                    if x == retries:
                        raise
                    else:
                        sleep = backoff_in_seconds * 2 ** x + random.uniform(0, 1)
                        if logger is not None:
                            logger.warn(f"[backoff] sleeping for {sleep}")
                        time.sleep(sleep)
                        x += 1

        return wrapper

    return rwb
