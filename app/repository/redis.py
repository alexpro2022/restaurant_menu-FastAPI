import pickle

from aioredis import Redis

from app.core import settings

from .base import ModelType

serializer = pickle


class BaseRedis:
    def __init__(self,
                 redis: Redis | None = None,
                 redis_key_prefix: str = '') -> None:
        self.redis = redis
        self.redis_key_prefix = redis_key_prefix

    async def flush_all(self) -> None:
        if self.redis is not None:
            await self.redis.flushall(asynchronous=True)

    async def get_obj(self, key: int | str, forced_key: bool = False) -> ModelType | None:
        if self.redis is not None:
            if forced_key:
                key = key
            else:
                key = (key if (isinstance(key, str) and key.startswith(self.redis_key_prefix))  # type: ignore
                       else f'{self.redis_key_prefix}{key}')
            cache = await self.redis.get(key)
            if cache:
                result = serializer.loads(cache)
                if result:
                    return result
        return None

    async def get_all(self) -> list[ModelType] | None:
        if self.redis is not None:
            result = [await self.get_obj(key) for key in  # type: ignore
                      await self.redis.keys(f'{self.redis_key_prefix}*')]
            if None not in result:
                return result  # type: ignore
        return None

    async def set_obj(self, obj: ModelType) -> None:
        if self.redis is not None and obj is not None:
            await self.redis.set(f'{self.redis_key_prefix}{obj.id}',
                                 serializer.dumps(obj),
                                 ex=settings.redis_expire)

    async def set_all(self, objs: list[ModelType]) -> None:
        if self.redis is not None and objs is not None:
            [await self.set_obj(obj) for obj in objs]  # type: ignore

    async def delete_obj(self, obj: ModelType) -> None:
        if self.redis is not None and obj is not None:
            await self.redis.delete(f'{self.redis_key_prefix}{obj.id}')
