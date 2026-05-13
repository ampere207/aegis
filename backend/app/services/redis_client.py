import redis.asyncio as redis
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        try:
            self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def set_task_status(self, task_id: str, status: str, metadata: dict = None):
        if not self.redis:
            return
        data = {"status": status}
        if metadata:
            data.update(metadata)
        await self.redis.hset(f"task:{task_id}", mapping=data)

    async def get_task_status(self, task_id: str):
        if not self.redis:
            return None
        return await self.redis.hgetall(f"task:{task_id}")

redis_client = RedisClient()
