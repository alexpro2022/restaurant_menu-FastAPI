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
                     extra_data: typing.Any | None = None) -> base.ModelType:
        await self.redis.flush()
        return await self.db.create(payload, extra_data=extra_data)

    async def update(self,
                     pk: int,
                     payload: typing.Any) -> base.ModelType:
        await self.redis.flush()
        return await self.db.update(pk, payload)

    async def delete(self, pk: int) -> dict:
        await self.redis.flush()
        return await self.db.delete(pk)
