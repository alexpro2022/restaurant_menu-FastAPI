import pickle
from typing import Any, Generic, TypeVar

from fastapi import HTTPException, status
from pydantic import BaseModel
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import Base

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBaseRepository(
    Generic[ModelType, CreateSchemaType, UpdateSchemaType]
):
    """Базовый класс для CRUD операций произвольных моделей."""
    OBJECT_ALREADY_EXISTS = 'Object with such a unique values already exists.'
    NOT_FOUND = 'Object(s) not found.'

    def __init__(self,
                 model: type[ModelType],
                 session: AsyncSession,
                 redis=None,
                 redis_key_prefix: str | None = None) -> None:
        self.model = model
        self.session = session
        self.redis = redis
        self.redis_key_prefix = redis_key_prefix

# === Read ===
    async def __get_by_attributes(
        self, *, all: bool = True, **kwargs,
    ) -> list[ModelType] | ModelType | None:
        query = (select(self.model).filter_by(**kwargs) if kwargs
                 else select(self.model))
        coro = self.session.scalars(query.order_by(self.model.id))
        if self.redis is None or kwargs.get('id') is None:
            result = await coro
            return result.all() if all else result.first()
        cache = ([await self.redis.get(key)
                  for key in self.redis.keys(f'{self.redis_key_prefix}*')]
                 if all else
                 await self.redis.get(f'{self.redis_key_prefix}{kwargs["id"]}')
                 )
        if cache is not None:
            return ([pickle.loads(obj) for obj in cache] if all else
                    pickle.loads(cache))
        result = await coro
        if all:
            result = result.all()
            for obj in result:
                await self.redis.set(
                    f'{self.redis_key_prefix}{obj.id}', pickle.dumps(obj))
        else:
            result = result.first()
            await self.redis.set(
                f'{self.redis_key_prefix}{result.id}', pickle.dumps(result))
        return result

    async def _get_all_by_attrs(self, *, exception: bool = False, **kwargs
                                ) -> list[ModelType] | None:
        """Raises `NOT_FOUND` exception if
           no objects are found and `exception=True`
           else returns None else returns list of found objects."""
        objects = await self.__get_by_attributes(**kwargs)
        if not objects:
            if exception:
                raise HTTPException(status.HTTP_404_NOT_FOUND, self.NOT_FOUND)
            return None
        return objects

    async def _get_by_attrs(self, *, exception: bool = False, **kwargs
                            ) -> ModelType | None:
        """Raises `NOT_FOUND` exception if
           no object is found and `exception=True`."""
        object = await self.__get_by_attributes(all=False, **kwargs)
        if object is None and exception:
            raise HTTPException(status.HTTP_404_NOT_FOUND, self.NOT_FOUND)
        return object  # type: ignore

    async def get(self, pk: int) -> ModelType | None:
        return await self._get_by_attrs(id=pk)

    async def get_or_404(self, pk: int) -> ModelType:
        return await self._get_by_attrs(id=pk, exception=True)  # type: ignore

    async def get_all(self, exception: bool = False) -> list[ModelType] | None:
        return await self._get_all_by_attrs(exception=exception)

# === Create, Update, Delete ===
    def has_permission(self, obj: ModelType, user: Any | None) -> None:
        """Check for user permission and raise exception if not allowed."""
        raise NotImplementedError('has_permission() must be implemented.')

    def is_update_allowed(self, obj: ModelType, payload: dict) -> None:
        """Check for custom conditions and raise exception if not allowed."""
        raise NotImplementedError('is_update_allowed() must be implemented.')

    def is_delete_allowed(self, obj: ModelType) -> None:
        """Check for custom conditions and raise exception if not allowed."""
        raise NotImplementedError('is_delete_allowed() must be implemented.')

    def perform_create(self, create_data: dict, extra_data: Any | None = None
                       ) -> None:
        """Modify create_data here if necessary.
        For instance if extra_data is user:
        ```py
        user = extra_data
        if user is not None:
           create_data['user_id'] = user.id
        ```
        """
        raise NotImplementedError('perform_create() must be implemented.')

    def perform_update(self, obj: ModelType, update_data: dict) -> ModelType:
        """Modify update_data here if necessary and return updated object."""
        raise NotImplementedError('perform_update() must be implemented.')

    async def _save(self, obj: ModelType) -> ModelType:
        """Tries to write object to DB. Raises `BAD_REQUEST` exception
           if object already exists in DB. """
        self.session.add(obj)
        try:
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                self.OBJECT_ALREADY_EXISTS)
        await self.session.refresh(obj)
        if self.redis is not None:
            await self.redis.set(
                f'{self.redis_key_prefix}{obj.id}', pickle.dumps(obj))
        return obj

    async def create(
        self, payload: CreateSchemaType, *, extra_data: Any | None = None
    ) -> ModelType:
        """perform_create method is called if extra_data is not None."""
        create_data = payload.dict()
        if extra_data is not None:
            self.perform_create(create_data, extra_data)
        return await self._save(self.model(**create_data))

    async def update(
        self,
        pk: int,
        payload: UpdateSchemaType,
        *,
        user: Any | None = None,
        perform_update: bool = False,
    ) -> ModelType:
        """perform_update method is called if perform_update=True
           else the object is updated as follows:
            ```py
            for key, value in update_data.items():
                setattr(obj, key, value)
            ```
        """
        obj = await self.get_or_404(pk)
        if user is not None:
            self.has_permission(obj, user)
        update_data = payload.dict(exclude_unset=True,
                                   exclude_none=True,
                                   exclude_defaults=True)
        self.is_update_allowed(obj, update_data)
        if perform_update:
            obj = self.perform_update(obj, update_data)
        else:
            for key, value in update_data.items():
                setattr(obj, key, value)
        return await self._save(obj)

    async def delete(self, pk: int, user: Any | None = None) -> ModelType:
        obj = await self.get_or_404(pk)
        if user is not None:
            self.has_permission(obj, user)
        self.is_delete_allowed(obj)
        await self.session.delete(obj)
        await self.session.commit()
        if self.redis is not None:
            self.redis.delete(f'{self.redis_key_prefix}{pk}')
        return obj
