"""
This is a base service class implementation.
Please provide methods  with extra logic for Redis in the inherited class.
"""
import typing

import pydantic

from app.repositories.base_db_repository import CRUDBaseRepository, ModelType
from app.repositories.redis_repository import RedisBaseRepository


class BaseService:
    MSG_NOT_IMPLEMENTED = "Method or function hasn't been implemented yet."

    def __init__(self, db: CRUDBaseRepository, redis: RedisBaseRepository):
        self.db = db
        self.redis = redis

    async def __get(self, method_name: str | None = None, pk: int | None = None) -> tuple[ModelType | None, bool]:
        """Returns obj, cache. Cache == True if obj from cache else False."""
        obj = (await self.redis.get_all() if pk is None else
               await self.redis.get_obj(pk))
        if obj:
            return obj, True
        obj = (await self.db.get_all() if pk is None else
               await self.db.__getattribute__(method_name)(pk))
        return obj, False

    async def get(self, pk: int) -> tuple[ModelType, bool]:
        """Returns obj, cache. Cache == True if obj from cache else False."""
        return await self.__get('get', pk)

    async def get_or_404(self, pk: int) -> tuple[ModelType, bool]:
        """Returns obj, cache. Cache == True if obj from cache else False."""
        return await self.__get('get_or_404', pk)

    async def get_all(self, exception: bool = False) -> tuple[list[ModelType] | None, bool]:
        """Returns objs, cache. Cache == True if obj from cache else False."""
        return await self.__get()

    async def set_cache(self, obj: ModelType | list[ModelType]) -> None:
        if obj:
            await self.redis.set_all(obj) if isinstance(obj, list) else await self.redis.set_obj(obj)

    async def create(self,
                     payload: pydantic.BaseModel,
                     extra_data: typing.Any | None = None) -> ModelType:
        """Base class provides database create method."""
        return await self.db.create(payload, extra_data=extra_data)

    async def update(self,
                     pk: int,
                     payload: pydantic.BaseModel) -> ModelType:
        """Base class provides database update method."""
        return await self.db.update(pk, payload)

    async def delete(self, pk: int) -> ModelType:
        """Base class provides database delete method."""
        return await self.db.delete(pk)

    async def set_cache_create(self):
        raise NotImplementedError(self.MSG_NOT_IMPLEMENTED)

    async def set_cache_update(self):
        raise NotImplementedError(self.MSG_NOT_IMPLEMENTED)

    async def set_cache_delete(self):
        raise NotImplementedError(self.MSG_NOT_IMPLEMENTED)
