import pickle

from aioredis import Redis

from .base_db_repository import ModelType

serializer = pickle


class BaseRedis:
    def __init__(self,
                 redis: Redis | None = None,
                 redis_key_prefix: str = '',
                 redis_expire: int = 3600) -> None:
        self.redis = redis
        self.redis_key_prefix = redis_key_prefix
        self.redis_expire: int = redis_expire

    async def get_obj(self, key: int | str) -> ModelType | None:
        if self.redis is not None:
            key = (key if (isinstance(key, str) and key.startswith(self.redis_key_prefix))  # type: ignore
                   else f'{self.redis_key_prefix}{key}')
            cache = await self.redis.get(key)
            if cache:
                result = serializer.loads(await self.redis.get(key))
                if result:
                    return result
        return None

    async def get_all(self) -> list[ModelType] | None:
        if self.redis is not None:
            result = [await self.get_obj(key.decode('utf-8')) for key in  # type: ignore
                      await self.redis.keys(f'{self.redis_key_prefix}*')]
            if result and None not in result:
                return result  # type: ignore
        return None

    async def set_obj(self, obj: ModelType) -> None:
        if self.redis is not None and obj is not None:
            await self.redis.set(f'{self.redis_key_prefix}{obj.id}',
                                 serializer.dumps(obj),
                                 ex=self.redis_expire)

    async def set_all(self, objs: list[ModelType]) -> None:
        if self.redis is not None and objs is not None:
            for obj in objs:
                await self.set_obj(obj)  # type: ignore

    async def delete_obj(self, obj: ModelType) -> None:
        if self.redis is not None and obj is not None:
            await self.redis.delete(f'{self.redis_key_prefix}{obj.id}')
