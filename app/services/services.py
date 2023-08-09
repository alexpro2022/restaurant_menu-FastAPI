import typing

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_aioredis, get_async_session
from app.models import Dish, Menu, Submenu
from app.repository import crud
from app.repository import redis as r

from ..repository import base as repo
from .base import BaseService

async_session = typing.Annotated[AsyncSession, Depends(get_async_session)]
redis = typing.Annotated[Redis, Depends(get_aioredis)]


def delete_response(model_name) -> dict:
    return {'status': True, 'message': f'The {model_name} has been deleted'}


class MenuService(BaseService):
    model_name = 'menu'

    def __init__(self, session: async_session, redis: redis):
        self.model_name = self.model_name.lower()
        super().__init__(crud.MenuRepository(session), r.BaseRedis(redis, self.model_name))
        self.submenu_redis = r.BaseRedis(redis, 'submenu')
        self.dish_redis = r.BaseRedis(redis, 'dish')

    async def get_all(self, exception: bool = False) -> list:
        menus: list[Menu] | None = await super().get_all(exception)
        return [] if menus is None else menus

    async def create(self,  # type: ignore [override]
                     payload: typing.Any,
                     extra_data: typing.Any | None = None) -> repo.ModelType:
        # creation in db and redis
        menu: Menu = await super().create(payload, extra_data)
        await self.redis.set_obj(menu)
        return menu

    async def update(self,  # type: ignore [override]
                     pk: int,
                     payload: typing.Any) -> repo.ModelType:
        menu: Menu = await super().update(pk, payload)
        await self.redis.set_obj(menu)
        return menu

    async def delete(self, pk: int) -> dict:  # type: ignore [override]
        # deletion from db and redis
        menu: Menu = await super().delete(pk)
        for submenu in menu.submenus:
            for dish in submenu.dishes:
                await self.dish_redis.delete_obj(dish)
            await self.submenu_redis.delete_obj(submenu)
        await self.redis.delete_obj(menu)
        return delete_response(self.model_name)


class SubmenuService(BaseService):
    model_name = 'submenu'

    def __init__(self, session: async_session, redis: redis):
        self.model_name = self.model_name.lower()
        super().__init__(crud.SubmenuRepository(session), r.BaseRedis(redis, self.model_name))
        self.menu_db = crud.MenuRepository(session)
        self.menu_redis = r.BaseRedis(redis, 'menu')
        self.dish_redis = r.BaseRedis(redis, 'dish')

    async def create(self,  # type: ignore [override]
                     payload: typing.Any,
                     extra_data: typing.Any | None = None) -> repo.ModelType:
        # creation in db
        submenu: Submenu = await super().create(payload, extra_data)
        # creation in redis and refreshing related models
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        for redis, item in ((self.menu_redis, menu), (self.redis, submenu)):
            await redis.set_obj(item)  # type: ignore [type-var]
        return submenu

    async def update(self,  # type: ignore [override]
                     pk: int,
                     payload: typing.Any) -> repo.ModelType:
        submenu: Submenu = await super().update(pk, payload)
        await self.redis.set_obj(submenu)
        return submenu

    async def delete(self, pk: int) -> dict:  # type: ignore [override]
        # deletion from db and redis
        submenu: Submenu = await super().delete(pk)
        for dish in submenu.dishes:
            await self.dish_redis.delete_obj(dish)
        await self.redis.delete_obj(submenu)
        # refreshing related models
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        await self.menu_redis.set_obj(menu)
        return delete_response(self.model_name)


class DishService(BaseService):
    model_name = 'dish'

    def __init__(self, session: async_session, redis: redis):
        self.model_name = self.model_name.lower()
        super().__init__(crud.DishRepository(session), r.BaseRedis(redis, self.model_name))
        self.submenu_db = crud.SubmenuRepository(session)
        self.submenu_redis = r.BaseRedis(redis, 'submenu')
        self.menu_db = crud.MenuRepository(session)
        self.menu_redis = r.BaseRedis(redis, 'menu')

    async def create(self,  # type: ignore [override]
                     payload: typing.Any,
                     extra_data: typing.Any | None = None) -> repo.ModelType:
        # creation in db
        dish: Dish = await super().create(payload, extra_data)
        # creation in redis and refreshing related models
        submenu: Submenu = await self.submenu_db.get_or_404(pk=dish.submenu_id)
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        for redis, item in ((self.menu_redis, menu), (self.submenu_redis, submenu), (self.redis, dish)):
            await redis.set_obj(item)  # type: ignore [type-var]
        return dish

    async def update(self,  # type: ignore [override]
                     pk: int,
                     payload: typing.Any) -> repo.ModelType:
        dish: Dish = await super().update(pk, payload)
        await self.redis.set_obj(dish)
        return dish

    async def delete(self, pk: int) -> dict:  # type: ignore [override]
        # deletion from db and redis
        dish: Dish = await super().delete(pk)
        await self.redis.delete_obj(dish)
        # refreshing related models
        submenu: Submenu = await self.submenu_db.get_or_404(pk=dish.submenu_id)
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        for redis, item in ((self.menu_redis, menu), (self.submenu_redis, submenu)):
            await redis.set_obj(item)  # type: ignore [type-var]
        return delete_response(self.model_name)
