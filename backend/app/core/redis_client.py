import redis
import json
from typing import Optional, Any
from app.core.config import settings

class RedisClient:
    """Redis client wrapper with serialization"""
    
    def __init__(self):
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5
        )
    
    def set(self, key: str, value: Any, expire: Optional[int] = None):
        """Set value with optional expiration"""
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        self.client.set(key, value, ex=expire)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except:
                return value
        return None
    
    def delete(self, key: str):
        """Delete key"""
        self.client.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def expire(self, key: str, seconds: int):
        """Set expiration"""
        self.client.expire(key, seconds)
    
    def lpush(self, key: str, *values):
        """Push to list"""
        self.client.lpush(key, *values)
    
    def lrange(self, key: str, start: int, end: int):
        """Get range from list"""
        return self.client.lrange(key, start, end)
    
    def keys(self, pattern: str):
        """Get keys matching pattern"""
        return self.client.keys(pattern)
    
    def ping(self) -> bool:
        """Check connection"""
        try:
            return self.client.ping()
        except:
            return False
    
    def close(self):
        """Close connection"""
        self.client.close()

# Singleton instance
redis_client = RedisClient()