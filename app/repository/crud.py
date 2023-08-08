from typing import Annotated, Any

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_aioredis, get_async_session
from app.models import Dish, Menu, Submenu

from .base import CRUDBaseRepository

async_session = Annotated[AsyncSession, Depends(get_async_session)]
redis = Annotated[Redis, Depends(get_aioredis)]


class CRUDRepository(CRUDBaseRepository):
    # the methods are not in use in the project
    def is_update_allowed(self, obj, payload) -> None:
        pass

    def is_delete_allowed(self, obj) -> None:
        pass


class MenuRepository(CRUDRepository):
    NOT_FOUND = 'menu not found'
    OBJECT_ALREADY_EXISTS = 'Меню с таким заголовком уже существует.'

    def __init__(self, session: async_session, redis: redis):
        super().__init__(Menu, session, redis, 'menu')

    async def get_all(self, exception: bool = False) -> list:
        menus = await super().get_all(exception)
        return [] if menus is None else menus

    async def delete(self, pk: int, user: Any | None = None) -> dict:
        await super().delete(pk, user)
        return {'status': True, 'message': 'The menu has been deleted'}


class SubmenuRepository(CRUDRepository):
    NOT_FOUND = 'submenu not found'
    OBJECT_ALREADY_EXISTS = 'Подменю с таким заголовком уже существует.'

    def __init__(self, session: async_session, redis: redis):
        super().__init__(Submenu, session, redis, 'submenu')

    def perform_create(self, create_data: dict, menu_id: int) -> None:  # type: ignore
        create_data['menu_id'] = menu_id

    async def delete(self, pk: int, user: Any | None = None) -> dict:
        await super().delete(pk, user)
        return {'status': True, 'message': 'The submenu has been deleted'}


class DishRepository(CRUDRepository):
    NOT_FOUND = 'dish not found'
    OBJECT_ALREADY_EXISTS = 'Блюдо с таким заголовком уже существует.'

    def __init__(self, session: async_session, redis: redis):
        super().__init__(Dish, session, redis, 'dish')

    def perform_create(self, create_data: dict, submenu_id: int) -> None:  # type: ignore
        create_data['submenu_id'] = submenu_id

    async def delete(self, pk: int, user: Any | None = None) -> dict:
        await super().delete(pk, user)
        return {'status': True, 'message': 'The dish has been deleted'}
