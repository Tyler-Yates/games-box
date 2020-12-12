import time


def get_time_millis() -> int:
    return int(round(time.time() * 1000))
