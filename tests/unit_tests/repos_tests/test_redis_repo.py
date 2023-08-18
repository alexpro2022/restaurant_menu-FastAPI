from time import sleep
from typing import Any
import pytest
import pytest_asyncio

from app.repositories.redis_repository import RedisBaseRepository
from tests import conftest as c
from tests.utils import compare, get_method


class TestBaseRedis:
    prefix = 'prefix:'
    redis: RedisBaseRepository

    @pytest_asyncio.fixture
    async def init(self, get_test_redis: c.FakeRedis) -> None:
        self.redis = RedisBaseRepository(get_test_redis, self.prefix)

    @pytest_asyncio.fixture
    async def init_expire(self, get_test_redis: c.FakeRedis) -> None:
        self.redis = RedisBaseRepository(get_test_redis, redis_expire=1)

    @pytest_asyncio.fixture
    async def obj_from_db(self, get_menu_repo: c.MenuRepository, menu: c.Response) -> c.Menu:
        objs = await get_menu_repo.get_all()
        assert isinstance(objs, list)
        assert len(objs) == 1
        return objs[0]

    @pytest_asyncio.fixture
    async def set_obj_get_from_redis(self, obj_from_db: c.Menu) -> c.Menu:
        return await self.__set_obj(obj_from_db)

    async def __set_obj(self, obj_from_db: c.Menu) -> c.Menu:
        assert await self.redis.set_obj(obj_from_db) is None
        obj = await self.redis.get_obj(obj_from_db.id)
        compare(obj, obj_from_db)
        return obj

    @pytest.mark.parametrize('method_name, method_param', (
        ('get_all', None),
        ('get_obj', 1),
        ('set_obj', 'obj_from_db'),
        ('set_all', '[obj_from_db]'),
        ('delete_obj', 'obj_from_db'),
    ))
    @c.pytest_mark_anyio
    async def test_methods_return_None(self, init, obj_from_db: c.Menu, method_name: str, method_param: str) -> None:
        method = get_method(self.redis, method_name)
        match method_param:
            case None:
                assert await method() is None
            case 'obj_from_db':
                assert await method(obj_from_db) is None
            case '[obj_from_db]':
                assert await method([obj_from_db]) is None
            case _:
                assert await method(method_param) is None

    @c.pytest_mark_anyio
    async def test_get_all_returns_list_objs(self, init, obj_from_db: c.Menu, set_obj_get_from_redis: c.Menu) -> None:
        objs = await self.redis.get_all()
        assert isinstance(objs, list)
        for obj in objs:
            compare(obj, obj_from_db)

    @c.pytest_mark_anyio
    async def test_get_obj_returns_obj(self, init, obj_from_db: c.Menu, set_obj_get_from_redis: c.Menu) -> None:
        obj = await self.redis.get_obj(obj_from_db.id)
        compare(obj, obj_from_db)

    @c.pytest_mark_anyio
    async def test_set_obj_expire(self, init_expire, set_obj_get_from_redis: c.Menu) -> None:
        obj = set_obj_get_from_redis
        assert await self.redis.get_obj(obj.id)
        sleep(1)
        assert await self.redis.get_obj(obj.id) is None

    @c.pytest_mark_anyio
    async def test_delete_obj(self, init, set_obj_get_from_redis: c.Menu) -> None:
        obj = set_obj_get_from_redis
        assert await self.redis.get_obj(obj.id)
        assert await self.redis.delete_obj(obj) is None
        assert await self.redis.get_obj(obj.id) is None

    @c.pytest_mark_anyio
    async def test_set_obj(self, init, obj_from_db: c.Menu) -> None:
        await self.__set_obj(obj_from_db)

    @c.pytest_mark_anyio
    async def test_set_all(self, init, obj_from_db: c.Menu) -> None:
        lst = [obj_from_db]
        assert await self.redis.get_all() is None
        assert await self.redis.set_all(lst) is None
        objs = await self.redis.get_all()
        assert len(objs) == len(lst)
        compare(objs[0], obj_from_db)

    @pytest.mark.parametrize('suffix', (1, 1.2, '1', [1, 2], (1, 2), {1, 1, 2}, {'1': 300}))
    def test_get_key(self, init, suffix: Any) -> None:
        key = self.redis._get_key(suffix)
        assert isinstance(key, str)
        assert key == f'{self.prefix}{suffix}'
