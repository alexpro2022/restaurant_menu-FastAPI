from http import HTTPStatus
from typing import Any, Generic, Type, TypeVar

from fastapi import HTTPException
from pydantic import BaseModel
from sqlalchemy import exc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import Base

try:
    from app.models import User
except ImportError:
    User = None

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    OBJECT_ALREADY_EXISTS = 'Object with such a unique values already exists.'
    NOT_FOUND = 'Object(s) not found.'

    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

# === Read ===
    async def __get_by_attribute(
        self,
        session: AsyncSession,
        attr_name: str,
        attr_value: Any,
    ):
        return await session.scalars(
            select(self.model).where(
                getattr(self.model, attr_name) == attr_value
            ).order_by(self.model.id))

    async def get_all_by_attr(
        self,
        session: AsyncSession,
        attr_name: str | None = None,
        attr_value: Any | None = None,
        exception: bool = False
    ) -> list[ModelType] | None:
        """Raises `NOT_FOUND` exception if
           no objects are found and `exception=True`."""
        if attr_name is not None and attr_value is not None:
            objs = await self.__get_by_attribute(
                session, attr_name, attr_value)
        else:
            objs = await session.scalars(select(self.model))
        objects = objs.all()
        if not objects and exception:
            raise HTTPException(HTTPStatus.NOT_FOUND, self.NOT_FOUND)
        return objects

    async def get_by_attr(
        self,
        session: AsyncSession,
        attr_name: str,
        attr_value: Any,
        exception: bool = False
    ) -> ModelType | None:
        """Raises `NOT_FOUND` exception if
           no object is found and `exception=True`."""
        objs = await self.__get_by_attribute(
            session, attr_name, attr_value)
        object = objs.first()
        if object is None and exception:
            raise HTTPException(HTTPStatus.NOT_FOUND, self.NOT_FOUND)
        return object

    async def get(
        self, session: AsyncSession, pk: int,
    ) -> ModelType | None:
        return await self.get_by_attr(session, 'id', pk)

    async def get_or_404(
        self, session: AsyncSession, pk: int,
    ) -> ModelType:
        return await self.get_by_attr(session, 'id', pk, exception=True)

    async def get_all(
        self, session: AsyncSession, exception: bool = False
    ) -> list[ModelType]:
        return await self.get_all_by_attr(session, exception=exception)

# === Create, Update, Delete ===
    def has_permission(self, obj: ModelType, user: User) -> None:
        """Check for user permission and raise exception if not allowed."""
        raise NotImplementedError('has_permission() must be implemented.')

    def is_update_allowed(self, obj: ModelType, payload: dict) -> None:
        """Check for custom conditions and raise exception if not allowed."""
        raise NotImplementedError('is_update_allowed() must be implemented.')

    def is_delete_allowed(self, obj: ModelType) -> None:
        """Check for custom conditions and raise exception if not allowed."""
        raise NotImplementedError('is_delete_allowed() must be implemented.')

    def perform_create(
            self, create_data: dict, user: User | None = None) -> None:
        """Modify create_data here if necessary. For instance:
        ```py
        if user is not None:
           create_data['user_id'] = user.id
        ```
        """
        raise NotImplementedError('perform_create() must be implemented.')

    def perform_update(self, obj: ModelType, update_data: dict) -> ModelType:
        """Modify update_data here if necessary and return updated object."""
        raise NotImplementedError('perform_update() must be implemented.')

    async def _save(
            self, session: AsyncSession, obj: ModelType) -> ModelType:
        """Tries to write object to DB. Raises `BAD_REQUEST` exception
           if object already exists in DB. """
        session.add(obj)
        try:
            await session.commit()
        except exc.IntegrityError:
            await session.rollback()
            raise HTTPException(
                HTTPStatus.BAD_REQUEST,
                self.OBJECT_ALREADY_EXISTS)
        await session.refresh(obj)
        return obj

    async def create(
        self,
        session: AsyncSession,
        payload: CreateSchemaType,
        *,
        user: User | None = None,
        perform_create: bool = True,
    ) -> ModelType:
        """perform_create method is called if perform_create=True."""
        create_data = payload.dict()
        if perform_create:
            self.perform_create(create_data, user)
        return await self._save(session, self.model(**create_data))

    async def update(
        self,
        session: AsyncSession,
        pk: int,
        payload: UpdateSchemaType,
        *,
        user: User | None = None,
        perform_update: bool = True,
    ) -> ModelType:
        """perform_update method is called if perform_update=True
           else the object is updated as follows:
            ```py
            for key in update_data:
                setattr(obj, key, update_data[key])
            ```
        """
        obj = await self.get_or_404(session, pk)
        if user is not None:
            self.has_permission(obj, user)
        update_data = payload.dict(
            exclude_unset=True,
            exclude_none=True,
            exclude_defaults=True)
        self.is_update_allowed(obj, update_data)
        if perform_update:
            obj = self.perform_update(obj, update_data)
        else:
            for key in update_data:
                setattr(obj, key, update_data[key])
        return await self._save(session, obj)

    async def delete(
        self,
        session: AsyncSession,
        pk: int,
        user: User | None = None,
    ) -> ModelType:
        obj = await self.get_or_404(session, pk)
        if user is not None:
            self.has_permission(obj, user)
        self.is_delete_allowed(obj)
        await session.delete(obj)
        await session.commit()
        return obj
