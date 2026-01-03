from redis.asyncio import Redis
import time


class RateLimiter:
    def __init__(
        self,
        redis: Redis,
        max_calls: int,
        period: int,
        prefix: str = "whatsapp:rate_limiter",
    ):
        self.redis = redis
        self.max_calls = max_calls
        self.period = period
        self.prefix = prefix

    async def is_allowed(self, user_id: str) -> bool:
        key = f"{self.prefix}:{user_id}"
        count = await self.redis.incr(key)
        if count == 1:
            await self.redis.expire(key, self.period)

        if count > self.max_calls:
            return False
        return True
