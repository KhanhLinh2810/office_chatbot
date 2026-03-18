from redis import Redis

from app.core.settings import settings

class CacheService:
    def __init__(self):
        self.instance = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True 
        )

    def set(self, key, value, ttl=1800000):
        self.instance.setex(key, ttl, value)

    def get(self, key):
        return self.instance.get(key)

    def delete(self, key):
        self.instance.delete(key)