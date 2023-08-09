"""
This is a base service class implementation with simple redis refreshing by deleting
all keys in all databases on the current host (using the flushall method for that).
This behavior might be acceptable in systems with few renewals (the ones servicing mostly GET requests).
If, however, this behavior is not applicable for your needs, please override the
create, update, and delete methods in the inherited class with the flush=False attr.
"""
import typing

from ..repository import base, redis


class BaseService:
    def __init__(self, db: base.CRUDBaseRepository, redis: redis.BaseRedis):
        self.db = db
        self.redis = redis

    async def get(self, pk: int) -> base.ModelType | None:
        obj = await self.redis.get_obj(pk)  # type: ignore
        if obj:
            return obj
        obj = await self.db.get(pk)
        if obj:
            await self.redis.set_obj(obj)
        return obj

    async def get_or_404(self, pk: int) -> base.ModelType:
        obj = await self.redis.get_obj(pk)  # type: ignore
        if obj:
            return obj
        obj = await self.db.get_or_404(pk)
        await self.redis.set_obj(obj)
        return obj

    async def get_all(self, exception: bool = False) -> list[base.ModelType] | None:
        objs = await self.redis.get_all()  # type: ignore
        if objs:
            return objs
        objs = await self.db.get_all(exception)
        if objs:
            await self.redis.set_all(objs)
        return objs

    async def create(self,
                     payload: typing.Any,
                     extra_data: typing.Any | None = None,
                     flush: bool = True) -> base.ModelType:
        if flush:
            await self.redis.flush_all()
        return await self.db.create(payload, extra_data=extra_data)

    async def update(self,
                     pk: int,
                     payload: typing.Any,
                     flush: bool = True) -> base.ModelType:
        if flush:
            await self.redis.flush_all()
        return await self.db.update(pk, payload)

    async def delete(self, pk: int, flush: bool = True) -> base.ModelType:
        if flush:
            await self.redis.flush_all()
        return await self.db.delete(pk)
