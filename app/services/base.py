"""
This is a base service class implementation.
Please override set_cache_xxx methods with extra logic for Redis in the inherited class.
    * xxx - create/update/delete
"""
import typing

import pydantic

from fastapi import BackgroundTasks
from app.repositories.base_db_repository import CRUDBaseRepository, ModelType
from app.repositories.redis_repository import RedisBaseRepository


class BaseService:
    """Base abstract service class."""
    MSG_NOT_IMPLEMENTED = "Method or function hasn't been implemented yet."

    def __init__(self, db: CRUDBaseRepository, redis: RedisBaseRepository, bg_tasks: BackgroundTasks | None = None):
        self.db = db
        self.redis = redis
        self.bg_tasks = bg_tasks

    async def _add_bg_task(self, method, obj: ModelType | list[ModelType]) -> None:
        if obj:
            self.bg_tasks.add_task(method, obj) if self.bg_tasks is not None else await method(obj)

    async def set_cache(self, obj: ModelType | list[ModelType]) -> None:
        if obj:
            await self.redis.set_all(obj) if isinstance(obj, list) else await self.redis.set_obj(obj)

    async def __get(self, method_name: str | None = None, pk: int | None = None) -> ModelType | None:
        obj = (await self.redis.get_all() if pk is None else
               await self.redis.get_obj(pk))
        if obj:
            return obj
        obj = (await self.db.get_all() if pk is None else
               await self.db.__getattribute__(method_name)(pk))
        await self._add_bg_task(self.set_cache, obj)
        return obj

    async def get(self, pk: int) -> tuple[ModelType, bool]:
        return await self.__get('get', pk)

    async def get_or_404(self, pk: int) -> tuple[ModelType, bool]:
        return await self.__get('get_or_404', pk)

    async def get_all(self, exception: bool = False) -> tuple[list[ModelType] | None, bool]:
        return await self.__get()

    async def set_cache_create(self, obj) -> None:
        raise NotImplementedError(self.MSG_NOT_IMPLEMENTED)

    async def set_cache_update(self, obj) -> None:
        raise NotImplementedError(self.MSG_NOT_IMPLEMENTED)

    async def set_cache_delete(self, obj) -> None:
        raise NotImplementedError(self.MSG_NOT_IMPLEMENTED)

    async def create(self,
                     payload: pydantic.BaseModel,
                     extra_data: typing.Any | None = None) -> ModelType:
        """Base class provides database create method and put a setting
        cache task to background."""
        obj = await self.db.create(payload, extra_data=extra_data)
        await self._add_bg_task(self.set_cache_create, obj)
        return obj

    async def update(self,
                     pk: int,
                     payload: pydantic.BaseModel) -> ModelType:
        """Base class provides database update method."""
        obj = await self.db.update(pk, payload)
        await self._add_bg_task(self.set_cache_update, obj)
        return obj

    async def delete(self, pk: int) -> ModelType:
        """Base class provides database delete method."""
        obj = await self.db.delete(pk)
        await self._add_bg_task(self.set_cache_delete, obj)
        return obj
