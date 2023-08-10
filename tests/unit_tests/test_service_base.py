import pytest
from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base_db_repository import CRUDBaseRepository
from app.repositories.redis_repository import RedisBaseRepository
from app.services.services import BaseService

from ..conftest import pytest_mark_anyio
from ..fixtures import data as d

pytestmark = pytest_mark_anyio


class TestBaseService:
    model = d.Model
    base_service: BaseService

    @pytest.fixture
    def setup_method(self, get_test_session, get_test_redis):
        self.base_service = BaseService(CRUDBaseRepository(self.model, get_test_session),
                                        RedisBaseRepository(get_test_redis))

    async def test_setup_method(self, setup_method):
        assert await self.base_service.db.get_all() is None
        assert await self.base_service.redis.get_all() is None


async def test_delete_menu(menu, get_menu_service):
    assert await get_menu_service.delete(menu.json()['id']) == d.DELETED_MENU


async def test_delete_submenu(submenu, get_submenu_service):
    assert await get_submenu_service.delete(submenu.json()['id']) == d.DELETED_SUBMENU


async def test_delete_dish(dish, get_dish_service):
    assert await get_dish_service.delete(dish.json()['id']) == d.DELETED_DISH
