from time import sleep

import pytest
from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.repository.base import CRUDBaseRepository
from app.repository.redis import BaseRedis
from app.services.services import BaseService

from ..conftest import pytest_mark_anyio
from ..fixtures import data as d


def info(item):
    print(item)
    assert False


class TestBaseRedis:
    redis: BaseRedis

    @pytest.fixture
    def setup_method(self, get_test_redis):
        self.redis = BaseRedis(get_test_redis)

    @pytest.fixture
    def setup_method_expire(self, get_test_redis):
        self.redis = BaseRedis(get_test_redis, redis_expire=1)

    def _compare(self, from_redis, from_db):
        assert from_redis.__table__.columns == from_db.__table__.columns
        for c in from_redis.__table__.columns:
            assert getattr(from_redis, c.key) == getattr(from_db, c.key)

    @pytest_mark_anyio
    async def test_set_obj(self, setup_method, get_menu_crud, menu):
        objs = await get_menu_crud.get_all()
        assert isinstance(objs, list)
        obj = objs[0]
        assert await self.redis.get_obj(obj.id) is None
        await self.redis.set_obj(obj)
        self._compare(await self.redis.get_obj(obj.id), obj)

    @pytest_mark_anyio
    async def test_set_obj_expire(self, setup_method_expire, get_menu_crud, menu):
        objs = await get_menu_crud.get_all()
        assert isinstance(objs, list)
        obj = objs[0]
        assert await self.redis.get_obj(obj.id) is None
        await self.redis.set_obj(obj)
        assert await self.redis.get_obj(obj.id) is not None
        sleep(1)
        assert await self.redis.get_obj(obj.id) is None
