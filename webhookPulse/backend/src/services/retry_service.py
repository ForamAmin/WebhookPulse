import random

from src.core.retry_config import (
    BASE_DELAY_SECONDS,
    JITTER_SECONDS,
    MAX_DELAY_SECONDS,
)


def calculate_retry_delay(attempt_number: int) -> float:
    exponential_delay = BASE_DELAY_SECONDS * (
        2 ** (attempt_number - 1)
    )

    exponential_delay = min(
        exponential_delay,
        MAX_DELAY_SECONDS,
    )

    jitter = random.uniform(
        0,
        JITTER_SECONDS,
    )

    return exponential_delay + jitter