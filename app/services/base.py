"""
This is a base service class implementation. Please override the
create, update, and delete methods in the inherited class with extra logic for Redis.
"""
import typing

from ..repositories.base_db_repository import CRUDBaseRepository, ModelType
from ..repositories.redis_repository import RedisBaseRepository


class BaseService:
    def __init__(self, db: CRUDBaseRepository, redis: RedisBaseRepository):
        self.db = db
        self.redis = redis

    async def get(self, pk: int) -> ModelType | None:
        obj = await self.redis.get_obj(pk)  # type: ignore
        if obj:
            return obj
        obj = await self.db.get(pk)
        if obj:
            await self.redis.set_obj(obj)
        return obj

    async def get_or_404(self, pk: int) -> ModelType:
        obj = await self.redis.get_obj(pk)  # type: ignore
        if obj:
            return obj
        obj = await self.db.get_or_404(pk)
        await self.redis.set_obj(obj)
        return obj

    async def get_all(self, exception: bool = False) -> list[ModelType] | None:
        objs = await self.redis.get_all()  # type: ignore
        if objs:
            return objs
        objs = await self.db.get_all(exception)
        if objs:
            await self.redis.set_all(objs)
        return objs

    async def create(self,
                     payload: typing.Any,
                     extra_data: typing.Any | None = None) -> ModelType:
        return await self.db.create(payload, extra_data=extra_data)

    async def update(self,
                     pk: int,
                     payload: typing.Any) -> ModelType:
        return await self.db.update(pk, payload)

    async def delete(self, pk: int) -> ModelType:
        return await self.db.delete(pk)
