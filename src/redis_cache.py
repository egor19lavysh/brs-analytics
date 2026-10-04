import pickle
from typing import Any

from redis import Redis


class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.client: Redis = Redis(host=host, port=port, db=db)

    def set(self, key: str, value: Any, ttl: int = 60) -> None:
        if not self.client:
            raise ValueError("Redis connection is not initialized.")
        if value is None:
            return
        self.client.set(key, pickle.dumps(value), ex=ttl)

    def get(self, key: str) -> Any | None:
        if not self.client:
            raise ValueError("Redis connection is not initialized.")
        value = self.client.get(key)
        return pickle.loads(value) if value is not None else None