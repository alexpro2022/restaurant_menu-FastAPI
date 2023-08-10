from time import sleep

import pytest
import pytest_asyncio

from app.repositories.redis_repository import RedisBaseRepository

from ..conftest import pytest_mark_anyio


class TestBaseRedis:
    prefix = 'prefix:'
    redis: RedisBaseRepository

    @pytest_asyncio.fixture
    async def init(self, get_test_redis):
        self.redis = RedisBaseRepository(get_test_redis, self.prefix)

    @pytest_asyncio.fixture
    async def init_expire(self, get_test_redis):
        self.redis = RedisBaseRepository(get_test_redis, redis_expire=1)

    @pytest_asyncio.fixture
    async def obj_from_db(self, get_menu_crud, menu):
        objs = await get_menu_crud.get_all()
        assert isinstance(objs, list)
        assert len(objs) == 1
        return objs[0]

    @pytest_asyncio.fixture
    async def set_obj_get_from_redis(self, obj_from_db):
        return await self.__set_obj(obj_from_db)

    async def __set_obj(self, obj_from_db):
        assert await self.redis.set_obj(obj_from_db) is None
        obj = await self.redis.get_obj(obj_from_db.id)
        self._compare(obj, obj_from_db)
        return obj

    def _compare(self, left, right) -> None:
        assert self and right
        assert left.__table__.columns == right.__table__.columns
        for c in left.__table__.columns:
            assert getattr(left, c.key) == getattr(right, c.key)

    @pytest_mark_anyio
    async def test_methods_return_None(self, init, obj_from_db):
        assert await self.redis.get_all() is None
        assert await self.redis.get_obj(1) is None
        assert await self.redis.get_obj(None) is None
        assert await self.redis.set_obj(obj_from_db) is None
        assert await self.redis.delete_obj(obj_from_db) is None
        assert await self.redis.set_all([obj_from_db]) is None

    @pytest_mark_anyio
    async def test_get_all_returns_list_objs(self, init, obj_from_db, set_obj_get_from_redis):
        objs = await self.redis.get_all()
        assert isinstance(objs, list)
        for obj in objs:
            self._compare(obj, obj_from_db)

    @pytest_mark_anyio
    async def test_get_obj_returns_obj(self, init, obj_from_db, set_obj_get_from_redis):
        obj = await self.redis.get_obj(obj_from_db.id)
        self._compare(obj, obj_from_db)

    @pytest_mark_anyio
    async def test_set_obj_expire(self, init_expire, set_obj_get_from_redis):
        obj = set_obj_get_from_redis
        assert await self.redis.get_obj(obj.id)
        sleep(1)
        assert await self.redis.get_obj(obj.id) is None

    @pytest_mark_anyio
    async def test_delete_obj(self, init, set_obj_get_from_redis):
        obj = set_obj_get_from_redis
        assert await self.redis.get_obj(obj.id)
        assert await self.redis.delete_obj(obj) is None
        assert await self.redis.get_obj(obj.id) is None

    @pytest_mark_anyio
    async def test_set_obj(self, init, obj_from_db):
        await self.__set_obj(obj_from_db)

    @pytest_mark_anyio
    async def test_set_all(self, init, obj_from_db):
        lst = [obj_from_db]
        assert await self.redis.get_all() is None
        assert await self.redis.set_all(lst) is None
        objs = await self.redis.get_all()
        assert len(objs) == len(lst)
        self._compare(objs[0], obj_from_db)

    @pytest.mark.parametrize('suffix', (1, 1.2, '1', [1, 2], (1, 2), {1, 1, 2}, {'1': 300}))
    def test_get_key(self, init, suffix) -> None:
        key = self.redis._get_key(suffix)
        assert isinstance(key, str)
        assert key == f'{self.prefix}{suffix}'
