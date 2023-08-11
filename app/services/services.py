import typing

from aioredis import Redis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_aioredis, get_async_session
from app.models import Dish, Menu, Submenu
from app.repositories.db_repository import (
    DishRepository,
    MenuRepository,
    SubmenuRepository,
)
from app.repositories.redis_repository import RedisBaseRepository
from app.services.base import BaseService

async_session = typing.Annotated[AsyncSession, Depends(get_async_session)]
redis = typing.Annotated[Redis, Depends(get_aioredis)]


class MenuService(BaseService):
    def __init__(self, session: async_session, redis: redis):
        super().__init__(MenuRepository(session), RedisBaseRepository(redis, 'menu'))
        self.submenu_redis = RedisBaseRepository(redis, 'submenu')
        self.dish_redis = RedisBaseRepository(redis, 'dish')

    async def set_cache_delete(self, menu: Menu) -> None:
        for submenu in menu.submenus:
            for dish in submenu.dishes:
                await self.dish_redis.delete_obj(dish)
            await self.submenu_redis.delete_obj(submenu)
        await self.redis.delete_obj(menu)


class SubmenuService(BaseService):
    def __init__(self, session: async_session, redis: redis):
        super().__init__(SubmenuRepository(session), RedisBaseRepository(redis, 'submenu'))
        self.menu_db = MenuRepository(session)
        self.menu_redis = RedisBaseRepository(redis, 'menu')
        self.dish_redis = RedisBaseRepository(redis, 'dish')

    async def set_cache_create(self, submenu: Submenu) -> None:
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        for redis, item in ((self.menu_redis, menu), (self.redis, submenu)):
            await redis.set_obj(item)  # type: ignore [type-var]

    async def set_cache_delete(self, submenu: Submenu) -> None:
        for dish in submenu.dishes:
            await self.dish_redis.delete_obj(dish)
        await self.redis.delete_obj(submenu)
        # refreshing related models
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        await self.menu_redis.set_obj(menu)


class DishService(BaseService):
    def __init__(self, session: async_session, redis: redis):
        super().__init__(DishRepository(session), RedisBaseRepository(redis, 'dish'))
        self.submenu_db = SubmenuRepository(session)
        self.submenu_redis = RedisBaseRepository(redis, 'submenu')
        self.menu_db = MenuRepository(session)
        self.menu_redis = RedisBaseRepository(redis, 'menu')

    async def set_cache_create(self, dish: Dish) -> None:
        submenu: Submenu = await self.submenu_db.get_or_404(pk=dish.submenu_id)
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        for redis, item in ((self.menu_redis, menu), (self.submenu_redis, submenu), (self.redis, dish)):
            await redis.set_obj(item)  # type: ignore [type-var]
        return dish

    async def set_cache_delete(self, dish: Dish) -> None:
        submenu: Submenu = await self.submenu_db.get_or_404(pk=dish.submenu_id)
        menu: Menu = await self.menu_db.get_or_404(pk=submenu.menu_id)
        for redis, item in ((self.menu_redis, menu), (self.submenu_redis, submenu)):
            await redis.set_obj(item)  # type: ignore [type-var]
