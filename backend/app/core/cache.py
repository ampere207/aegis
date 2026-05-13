import json
import logging
import functools
from typing import Any, Callable
from .config import settings
from ..services.redis_client import RedisClient

logger = logging.getLogger(__name__)

def cache_response(key_prefix: str, expire: int = 3600):
    """Decorator to cache function responses in Redis."""
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not settings.REDIS_URL:
                return await func(*args, **kwargs)
            
            # Create a stable cache key
            key_data = {
                "args": args[1:] if args and hasattr(args[0], '__class__') else args, # Skip 'cls' or 'self'
                "kwargs": kwargs
            }
            key = f"{key_prefix}:{hash(json.dumps(key_data, sort_keys=True))}"
            
            try:
                # Try to get from cache
                cached = await RedisClient.get(key)
                if cached:
                    logger.debug(f"Cache hit for {key}")
                    return json.loads(cached)
            except Exception as e:
                logger.error(f"Cache read error: {e}")

            # Execute function
            result = await func(*args, **kwargs)
            
            try:
                # Save to cache
                await RedisClient.set(key, json.dumps(result), expire)
                logger.debug(f"Cache write for {key}")
            except Exception as e:
                logger.error(f"Cache write error: {e}")
                
            return result
        return wrapper
    return decorator
