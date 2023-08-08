import typing

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_aioredis, get_async_session
from app.models import Menu
from app.repository import crud
from app.repository import redis as r

from .base import BaseService

async_session = typing.Annotated[AsyncSession, Depends(get_async_session)]
redis = typing.Annotated[Redis, Depends(get_aioredis)]


class GenericService(BaseService):
    model_name: str = ''

    async def delete(self, pk: int) -> dict:
        await super().delete(pk)
        return {'status': True, 'message': f'The {self.model_name} has been deleted'}


class MenuService(GenericService):
    model_name = 'menu'

    def __init__(self, session: async_session, redis: redis):
        self.model_name = self.model_name.lower()
        self.db = crud.MenuRepository(session)
        self.redis = r.BaseRedis(redis, self.model_name)

    async def get_all(self, exception: bool = False) -> list:
        menus: list[Menu] | None = await super().get_all(exception)
        return [] if menus is None else menus


class SubmenuService(GenericService):
    model_name = 'submenu'

    def __init__(self, session: async_session, redis: redis):
        self.db = crud.SubmenuRepository(session)
        self.redis = r.BaseRedis(redis, self.model_name)


class DishService(GenericService):
    model_name = 'dish'

    def __init__(self, session: async_session, redis: redis):
        self.model_name = self.model_name.lower()
        self.db = crud.DishRepository(session)
        self.redis = r.BaseRedis(redis, self.model_name)
