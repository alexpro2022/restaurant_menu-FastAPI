from time import sleep

import pytest_asyncio

from app.repositories.redis_repository import BaseRedis

from ..conftest import pytest_mark_anyio

pytestmark = pytest_mark_anyio


class TestBaseRedis:
    redis: BaseRedis

    @pytest_asyncio.fixture
    async def setup_method(self, get_test_redis):
        self.redis = BaseRedis(get_test_redis)

    @pytest_asyncio.fixture
    async def setup_method_expire(self, get_test_redis):
        self.redis = BaseRedis(get_test_redis, redis_expire=1)

    @pytest_asyncio.fixture
    async def obj_from_db(self, get_menu_crud, menu):
        objs = await get_menu_crud.get_all()
        assert isinstance(objs, list)
        assert len(objs) == 1
        return objs[0]

    @pytest_asyncio.fixture
    async def set_obj_get_from_redis(self, obj_from_db):
        await self.redis.set_obj(obj_from_db)
        obj = await self.redis.get_obj(obj_from_db.id)
        self._compare(obj, obj_from_db)
        return obj

    def _compare(self, left, right) -> None:
        assert left.__table__.columns == right.__table__.columns
        for c in left.__table__.columns:
            assert getattr(left, c.key) == getattr(right, c.key)

    async def test_get_methods_return_None(self, setup_method):
        assert await self.redis.get_all() is None
        assert await self.redis.get_obj(1) is None

    async def test_get_all_returns_list_objs(self, setup_method, obj_from_db, set_obj_get_from_redis):
        objs = await self.redis.get_all()
        assert isinstance(objs, list)
        self._compare(objs[0], obj_from_db)

    async def test_get_obj_returns_obj(self, setup_method, obj_from_db, set_obj_get_from_redis):
        obj = await self.redis.get_obj(obj_from_db.id)
        self._compare(obj, obj_from_db)

    async def test_set_obj_expire(self, setup_method_expire, obj_from_db, set_obj_get_from_redis):
        assert await self.redis.get_obj(obj_from_db.id)
        sleep(1)
        assert await self.redis.get_obj(obj_from_db.id) is None

    async def test_delete_obj(self, setup_method, obj_from_db, set_obj_get_from_redis):
        assert await self.redis.get_obj(obj_from_db.id)
        await self.redis.delete_obj(obj_from_db)
        assert await self.redis.get_obj(obj_from_db.id) is None
