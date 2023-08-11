import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.repositories.redis_repository import RedisBaseRepository
from app.services.services import BaseService
from tests.conftest import info, pytest_mark_anyio
from tests.fixtures import data as d
from tests.unit_tests.repos_tests.test_base_crud import CRUD
from tests.utils import compare

pytestmark = pytest_mark_anyio


class TestBaseService:
    model = d.Model
    schema = d.Schema
    base_service: BaseService
    post_payload = {'title': 'My object', 'description': 'My object description'}
    update_payload = {'title': 'My updated object', 'description': 'My updated object description'}

    async def _db_empty(self) -> bool:
        db = self.base_service.db
        assert isinstance(db, CRUD)
        return await db.get_all() is None

    async def _cache_empty(self) -> bool:
        r = self.base_service.redis
        assert isinstance(r, RedisBaseRepository)
        return await r.get_all() is None

    @pytest_asyncio.fixture
    async def init(self, get_test_session, get_test_redis):
        self.base_service = BaseService(CRUD(self.model, get_test_session),
                                        RedisBaseRepository(get_test_redis))
        assert await self._db_empty()
        assert await self._cache_empty()

    @pytest_asyncio.fixture
    async def get_obj_from_db(self, init) -> d.Model:
        obj = await self.base_service.db._save(self.model(**self.post_payload))
        assert not await self._db_empty()
        assert await self._cache_empty()
        return obj

    async def test_set_cache_obj(self, get_obj_from_db):
        assert await self._cache_empty()
        await self.base_service.set_cache(get_obj_from_db)
        assert not await self._cache_empty()

    async def test_set_cache_objs(self, get_obj_from_db):
        assert await self._cache_empty()
        await self.base_service.set_cache([get_obj_from_db])
        assert not await self._cache_empty()

    async def test_get(self, get_obj_from_db):
        # test returns obj, cache == None, False
        assert await self._cache_empty()
        assert await self.base_service.get(get_obj_from_db.id + 1) == (None, False)
        assert await self._cache_empty()
        # test returns object from db, cache == False
        obj, cache = await self.base_service.get(get_obj_from_db.id)
        compare(obj, get_obj_from_db)
        assert not cache
        assert await self._cache_empty()
        # test returns object from cache, cache == True
        await self.base_service.redis.set_obj(get_obj_from_db)
        obj, cache = await self.base_service.get(get_obj_from_db.id)
        compare(obj, get_obj_from_db)
        assert cache
        assert not await self._cache_empty()

    async def test_get_or_404(self, get_obj_from_db):
        # test raises exception if no object is found
        with pytest.raises(HTTPException):
            await self.base_service.get_or_404(get_obj_from_db.id + 1)
        # test returns object from db, cache == False
        obj, cache = await self.base_service.get_or_404(get_obj_from_db.id)
        compare(obj, get_obj_from_db)
        assert not cache
        assert await self._cache_empty()
        # test returns object from cache, cache == True
        await self.base_service.redis.set_obj(get_obj_from_db)
        obj, cache = await self.base_service.get_or_404(get_obj_from_db.id)
        compare(obj, get_obj_from_db)
        assert cache
        assert not await self._cache_empty()

    async def test_get_all_returns_None(self, init):
        # test returns obj, cache == None, False
        assert await self._cache_empty()
        assert await self.base_service.get_all() == (None, False)
        assert await self._cache_empty()

    async def test_get_all(self, get_obj_from_db):
        # test returns object from db, cache == False
        objs, cache = await self.base_service.get_all()
        assert isinstance(objs, list)
        compare(objs[0], get_obj_from_db)
        assert not cache
        assert await self._cache_empty()
        # test returns object from cache, cache == True
        await self.base_service.redis.set_all([get_obj_from_db])
        objs, cache = await self.base_service.get_all()
        assert isinstance(objs, list)
        compare(objs[0], get_obj_from_db)
        assert cache
        assert not await self._cache_empty()

    async def test_create(self, init):
        assert await self._db_empty()
        assert await self._cache_empty()
        await self.base_service.create(self.schema(**self.post_payload))
        assert not await self._db_empty()
        assert await self._cache_empty()

    async def test_update(self, get_obj_from_db):
        assert not await self._db_empty()
        assert await self._cache_empty()
        await self.base_service.update(get_obj_from_db.id, self.schema(**self.update_payload))
        assert not await self._db_empty()
        assert await self._cache_empty()

    async def test_delete(self, get_obj_from_db):
        assert not await self._db_empty()
        assert await self._cache_empty()
        await self.base_service.delete(get_obj_from_db.id)
        assert await self._db_empty()
        assert await self._cache_empty()
