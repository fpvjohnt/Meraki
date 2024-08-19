import asyncio
import time
from src.utils.logger import logger

class RateLimiter:
    def __init__(self, rate_limit: int, time_period: float = 1.0):
        self.rate_limit: int = rate_limit
        self.time_period: float = time_period
        self.tokens: float = rate_limit
        self.updated_at: float = time.monotonic()

    async def acquire(self) -> None:
        while True:
            now = time.monotonic()
            time_passed = now - self.updated_at
            self.tokens += time_passed * (self.rate_limit / self.time_period)
            if self.tokens > self.rate_limit:
                self.tokens = self.rate_limit
            self.updated_at = now

            if self.tokens >= 1:
                self.tokens -= 1
                return

            sleep_time = (1 - self.tokens) / (self.rate_limit / self.time_period)
            logger.debug(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds")
            await asyncio.sleep(sleep_time)